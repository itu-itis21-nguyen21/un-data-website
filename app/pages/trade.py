from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_required, current_user
from database import connection

trade_bp = Blueprint('trade', __name__)

def get_trade_details(offset=0, limit=10):
    cursor = connection.cursor(dictionary=True)
    sql_string = f"""
        SELECT
            trade.id AS id,
            countries.country AS country_name,
            series.series AS series,
            trade.val AS value,
            series.unit AS unit,
            trade.recordYear AS record_year,
            sources.source AS source

        FROM trade 
        JOIN countries ON trade.countryCode = countries.countryCode
        JOIN series ON trade.seriesID = series.seriesID
        JOIN sources ON trade.sourceID = sources.sourceID
        
        ORDER BY id ASC
        LIMIT {limit} OFFSET {offset};
    """
    cursor.execute(sql_string)
    result = cursor.fetchall()
    cursor.close()
    return result

@trade_bp.route('/trade', methods=['GET'])
@login_required
def page1():
    # Get the current page from query parameters; default to 1 if not provided
    current_page = int(request.args.get('page', 1))
    if current_page < 1:  # Ensure the page number is not less than 1
        current_page = 1

    # Calculate the offset for the SQL query
    limit = 10
    offset = (current_page - 1) * limit

    # Fetch trade details for the current page
    trade_details = get_trade_details(offset=offset, limit=limit)

    return render_template(
        'trade.html',
        details=trade_details,
        current_page=current_page,
        is_admin=(current_user.id == "admin")
    )

@trade_bp.route('/trade/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if current_user.id != "admin":
        return redirect('/trade')
    
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

        # Insert into the trade table
        sql = """
            INSERT INTO trade (countryCode, seriesID, val, recordYear, sourceID)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (country_code, series_id, value, record_year, source_id))
        connection.commit()
        cursor.close()

        return redirect('/trade')
    
    # Fetch country names only (not tuples)
    cursor.execute("SELECT country FROM countries ORDER BY country")
    countries = [row[0] for row in cursor.fetchall()]  # Extract the first element of each tuple

    cursor.execute("SELECT DISTINCT series FROM series INNER JOIN trade ON series.seriesID = trade.seriesID")
    series = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT source FROM sources INNER JOIN trade ON sources.sourceID = trade.sourceID")
    sources = [row[0] for row in cursor.fetchall()]

    cursor.close()
    
    referrer = request.referrer
    return render_template('add.html', countries=countries, series=series, sources=sources, referrer=referrer)

@trade_bp.route('/trade/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    if current_user.id != "admin":
        return redirect('/trade')
    if request.method == 'POST':
        value = request.form['value']
        record_year = request.form['record_year']
        
        cursor = connection.cursor()
        sql = """
            UPDATE trade
            SET val = %s, recordYear = %s
            WHERE id = %s
        """
        cursor.execute(sql, (value, record_year, record_id))
        connection.commit()
        cursor.close()
        
        return redirect('/trade')
    
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT * FROM trade WHERE id = %s"
    cursor.execute(sql, (record_id,))
    record = cursor.fetchone()
    cursor.close()
    
    referrer = request.referrer
    return render_template('edit.html', record=record, is_admin=(current_user.id == "admin"), referrer=referrer)

@trade_bp.route('/trade/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    if current_user.id != "admin":
        return redirect('/trade')
    cursor = connection.cursor()
    sql = "DELETE FROM trade WHERE id = %s"
    cursor.execute(sql, (record_id,))
    connection.commit()
    cursor.close()
    
    session["current_page"] = 1
    return redirect('/trade')

@trade_bp.route('/trade/search', methods=['GET'])
@login_required
def search_by_country_and_series():
    country_name = request.args.get('country_name', '').strip()
    series_name = request.args.get('series_name', '').strip()
    
    # Build the query dynamically based on provided filters
    filters = []
    query = """
        SELECT
            trade.id AS id,
            countries.country AS country_name,
            series.series AS series,
            trade.val AS value,
            series.unit AS unit,
            trade.recordYear AS record_year,
            sources.source AS source
        FROM trade
        JOIN countries ON trade.countryCode = countries.countryCode
        JOIN series ON trade.seriesID = series.seriesID
        JOIN sources ON trade.sourceID = sources.sourceID
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

    # Render results
    return render_template('trade.html', details=results, current_page=current_page, is_admin=(current_user.id == "admin"))


@trade_bp.route('/trade/next', methods=['POST'])
def next_record():
    cursor = connection.cursor(dictionary=True)
    # Example of incrementing the offset (assuming you store current page in session)
    current_page = session.get('current_page', 1) + 1
    offset = (current_page - 1) * 10
    sql = f"""
        SELECT
            trade.id AS id,
            countries.country AS country_name,
            series.series AS series,
            trade.val AS value,
            series.unit AS unit,
            trade.recordYear AS record_year,
            sources.source AS source
        FROM trade 
        JOIN countries ON trade.countryCode = countries.countryCode
        JOIN series ON trade.seriesID = series.seriesID
        JOIN sources ON trade.sourceID = sources.sourceID
        ORDER BY id ASC
        LIMIT 10 OFFSET {offset};
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    
    # Update session and re-render the page
    session['current_page'] = current_page
    return render_template(
        'trade.html',
        details=results,
        is_admin=(current_user.id == "admin"),
        referrer=request.referrer or '/trade'
    )


@trade_bp.route('/trade/previous', methods=['POST'])
def previous_record():
    cursor = connection.cursor(dictionary=True)
    current_page = session.get('current_page', 1)

    # Ensure we don't go below page 1
    if current_page > 1:
        current_page -= 1

    offset = (current_page - 1) * 10
    sql = f"""
        SELECT
            trade.id AS id,
            countries.country AS country_name,
            series.series AS series,
            trade.val AS value,
            series.unit AS unit,
            trade.recordYear AS record_year,
            sources.source AS source
        FROM trade
        JOIN countries ON trade.countryCode = countries.countryCode
        JOIN series ON trade.seriesID = series.seriesID
        JOIN sources ON trade.sourceID = sources.sourceID
        ORDER BY id ASC
        LIMIT 10 OFFSET {offset};
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

    # Update session and re-render the page
    session['current_page'] = current_page
    return render_template(
        'trade.html',
        details=results,
        is_admin=(current_user.id == "admin"),
        referrer=request.referrer or '/trade'
    )
