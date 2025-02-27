from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_required, current_user
from database import connection

health_bp = Blueprint('health', __name__)

def get_health_details(offset=0, limit=10):
    cursor = connection.cursor(dictionary=True)
    #show: id, countryName, recordYear, Series,series unit, val, source
    sql_string = """
        SELECT
            health.id AS id,
            countries.country AS country_name,
            series.series AS series,
            health.val AS value,
            series.unit AS unit,
            health.recordYear AS record_year,
            sources.source AS source

        FROM health 
        JOIN countries ON health.countryCode = countries.countryCode
        JOIN series ON health.seriesID = series.seriesID
        JOIN sources ON health.sourceID = sources.sourceID
        ORDER BY id ASC
        LIMIT %s OFFSET %s;

    """
    cursor.execute(sql_string, (limit, offset))
    result = cursor.fetchall()
    cursor.close()
    return result

@health_bp.route('/health', methods=['GET'])
@login_required
def page1():
    # Get the current page from query parameters; default to 1 if not provided
    current_page = int(request.args.get('page', 1))
    if current_page < 1:  # Ensure the page number is not less than 1
        current_page = 1

    # Calculate the offset for the SQL query
    limit = 10
    offset = (current_page - 1) * limit

    # Fetch health details for the current page
    health_details = get_health_details(offset=offset, limit=limit)

    return render_template(
        'health.html',
        details=health_details,
        current_page=current_page,
        is_admin=(current_user.id == "admin")
    )

@health_bp.route('/health/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if current_user.id != "admin":
        return redirect('/health')
    
    cursor = connection.cursor()

    if request.method == 'POST':
        # Retrieve form data
        country_name = request.form['country_name']
        series = request.form['series']
        value = request.form['value']
        record_year = request.form['record_year']
        source = request.form['source']

        # Get the corresponding country code from the database
        cursor.execute("SELECT countryCode FROM countries WHERE country = %s", (country_name,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return "Error: Selected country does not exist in the database.", 400
        country_code = result[0]
        
        cursor.execute("SELECT seriesID FROM series WHERE series = %s", (series,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return "Error: Selected series does not exist in the database.", 400
        series_id = result[0]

        cursor.execute("SELECT sourceID FROM sources WHERE source = %s", (source,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return "Error: Selected source does not exist in the database.", 400
        source_id = result[0]

        # Insert into the health table
        sql = """
            INSERT INTO health (countryCode, seriesID, val, recordYear, sourceID)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (country_code, series_id, value, record_year, source_id))
        connection.commit()
        cursor.close()

        return redirect('/health')
    
    # Fetch country names only (not tuples)
    cursor.execute("SELECT country FROM countries ORDER BY country")
    countries = [row[0] for row in cursor.fetchall()]  # Extract the first element of each tuple

    cursor.execute("SELECT DISTINCT series FROM series INNER JOIN health ON series.seriesID = health.seriesID")
    series = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT source FROM sources INNER JOIN health ON sources.sourceID = health.sourceID")
    sources = [row[0] for row in cursor.fetchall()]

    cursor.close()

    referrer = request.referrer
    return render_template('add.html', countries=countries, series=series, sources=sources, referrer=referrer)

@health_bp.route('/health/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    if current_user.id != "admin":
        return redirect('/health')
    if request.method == 'POST':
        value = request.form['value']
        record_year = request.form['record_year']
        
        cursor = connection.cursor()
        sql = """
            UPDATE health
            SET val = %s, recordYear = %s
            WHERE id = %s
        """
        cursor.execute(sql, (value, record_year, record_id))
        connection.commit()
        cursor.close()
        
        return redirect('/health')
    
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM health WHERE id = %s"
    cursor.execute(sql, (record_id,))
    record = cursor.fetchone()
    cursor.close()
    
    referrer = request.referrer
    return render_template('edit.html', record=record, is_admin=(current_user.id == "admin"), referrer=referrer)

@health_bp.route('/health/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    if current_user.id != "admin":
        return redirect('/health')
    cursor = connection.cursor()
    sql = "DELETE FROM health WHERE id = %s"
    cursor.execute(sql, (record_id,))
    connection.commit()
    cursor.close()
    
    session["current_page"] = 1
    return redirect('/health')

@health_bp.route('/health/search', methods=['GET'])
@login_required
def search_by_country_and_series():
    country_name = request.args.get('country_name', '').strip()
    series_name = request.args.get('series_name', '').strip()
    
    # Build the query dynamically based on provided filters
    filters = []
    query = """
        SELECT
            health.id AS id,
            countries.country AS country_name,
            series.series AS series,
            health.val AS value,
            series.unit AS unit,
            health.recordYear AS record_year,
            sources.source AS source
        FROM health
        JOIN countries ON health.countryCode = countries.countryCode
        JOIN series ON health.seriesID = series.seriesID
        JOIN sources ON health.sourceID = sources.sourceID
    """
    
    # Apply filters dynamically
    filters = []
    params = []

    if country_name:
            filters.append("countries.country LIKE %s")
            params.append(f"%{country_name}%")
    if series_name:
            filters.append("series.series = %s")
            params.append(series_name)

    # Append filters to query if present
    if filters:
            query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY id ASC"

    # Execute the query
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()

    # Define the current page explicitly for rendering
    current_page = session.get('current_page', 1)
    
    # Render the filtered results
    return render_template('health.html', details=results, current_page=current_page, is_admin=(current_user.id == "admin"))


@health_bp.route('/health/next', methods=['POST'])
def next_record():
    cursor = connection.cursor(dictionary=True)
    # Example of incrementing the offset (assuming you store current page in session)
    current_page = session.get('current_page', 1) + 1
    offset = (current_page - 1) * 10
    sql = f"""
        SELECT
            health.id AS id,
            countries.country AS country_name,
            series.series AS series,
            health.val AS value,
            series.unit AS unit,
            health.recordYear AS record_year,
            sources.source AS source

        FROM health 
        JOIN countries ON health.countryCode = countries.countryCode
        JOIN series ON health.seriesID = series.seriesID
        JOIN sources ON health.sourceID = sources.sourceID
        ORDER BY id ASC
        LIMIT 10 OFFSET {offset};
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

    # Update session and re-render the page
    session['current_page'] = current_page
    return render_template(
        'health.html',
        details=results,
        is_admin=(current_user.id == "admin"),
        referrer=request.referrer or '/health'
    )


@health_bp.route('/health/previous', methods=['POST'])
def previous_record():
    cursor = connection.cursor(dictionary=True)
    current_page = session.get('current_page', 1)

    # Ensure we don't go below page 1
    if current_page > 1:
        current_page -= 1

    offset = (current_page - 1) * 10
    sql = f"""
        SELECT
            health.id AS id,
            countries.country AS country_name,
            series.series AS series,
            health.val AS value,
            series.unit AS unit,
            health.recordYear AS record_year,
            sources.source AS source

        FROM health 
        JOIN countries ON health.countryCode = countries.countryCode
        JOIN series ON health.seriesID = series.seriesID
        JOIN sources ON health.sourceID = sources.sourceID
        ORDER BY id ASC
        LIMIT 10 OFFSET {offset};
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

    # Update session and re-render the page
    session['current_page'] = current_page
    return render_template(
        'health.html',
        details=results,
        is_admin=(current_user.id == "admin"),
        referrer=request.referrer or '/health'
    )