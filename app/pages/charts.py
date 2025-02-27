from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_required, current_user
from database import connection
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import circlify

charts_bp = Blueprint('charts', __name__)

def total_emission():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        SUM(C2.val) AS Total_CO2_Emission
    FROM
        carbondioxide C2
    WHERE
        C2.recordYear = 2020 AND
        C2.seriesID = 1;
    '''
    cursor.execute(query)
    results = int(cursor.fetchone()["Total_CO2_Emission"])
    cursor.close()

    return results

def avg_internet():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        ROUND(AVG(I.val), 1) AS avg_internet
    FROM
        internet I
    WHERE
        I.recordYear = 2020 AND
        I.seriesID = 14;
    '''
    cursor.execute(query)
    results = cursor.fetchone()["avg_internet"]
    cursor.close()

    return results

def total_trade():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        SUM(T.val) AS total_trade
    FROM
        trade T
    WHERE
        T.recordYear = 2020 AND
        (T.seriesID = 11 OR T.seriesID = 12);
    '''
    cursor.execute(query)
    results = cursor.fetchone()["total_trade"]
    cursor.close()

    return results

def emission_by_regions():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        R.region,
        SUM(C2.val) AS Total_CO2_Emission
    FROM
        carbondioxide C2
    JOIN
        countries C
        ON C2.countryCode = C.countryCode
    JOIN
        regions R
        ON C.regionCode = R.regionCode
    WHERE
        C2.recordYear = 2020 AND
        C2.seriesID = 1
    GROUP BY
        R.region,
        C2.recordYear
    ORDER BY
        R.region;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def emission_by_regions_over_years():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        R.region,
        C2.recordYear,
        SUM(C2.val) AS Total_CO2_Emission
    FROM
        carbondioxide C2
    JOIN
        countries C
        ON C2.countryCode = C.countryCode
    JOIN
        regions R
        ON C.regionCode = R.regionCode
    WHERE
        C2.seriesID = 1 AND
        C2.recordYear <= 2020 AND
        C2.recordYear MOD 5 = 0
    GROUP BY
        R.region,
        C2.recordYear
    ORDER BY
        R.region,
        C2.recordYear;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def top10_emission_by_countries():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        C.country,
        C2.val
    FROM
        carbondioxide C2
    JOIN
        countries C
        ON C2.countryCode = C.countryCode
    WHERE
        C2.seriesID = 1 AND
        C2.recordYear = 2020
    ORDER BY
        C2.val DESC
    LIMIT 10;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def top10_emission_per_capita_by_countries():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        C.country,
        C2.val
    FROM
        carbondioxide C2
    JOIN
        countries C
        ON C2.countryCode = C.countryCode
    WHERE
        C2.seriesID = 2 AND
        C2.recordYear = 2020
    ORDER BY
        C2.val DESC
    LIMIT 10;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def internet_by_regions():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        R.region,
        AVG(I.val) AS avg_internet_usage
    FROM
        internet I
    JOIN
        countries C
        ON I.countryCode = C.countryCode
    JOIN
        regions R
        ON C.regionCode = R.regionCode
    WHERE
        I.recordYear = 2020 AND
        I.seriesID = 14
    GROUP BY
        R.region
    ORDER BY
        R.region;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def internet_by_regions_over_years():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        R.region,
        I.recordYear,
        AVG(I.val) AS avg_internet_usage
    FROM
        internet I
    JOIN
        countries C
        ON I.countryCode = C.countryCode
    JOIN
        regions R
        ON C.regionCode = R.regionCode
    WHERE
        I.recordYear <= 2020 AND
        I.seriesID = 14
    GROUP BY
        R.region,
        I.recordYear
    ORDER BY
        R.region,
        I.recordYear;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def internet_all_data():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        C.country,
        I.val
    FROM
        internet I
    JOIN
        countries C
        ON I.countryCode = C.countryCode
    WHERE
        I.recordYear = 2020 AND
        I.seriesID = 14
    LIMIT 50;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def imports_by_regions():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        R.region,
        SUM(T.val) AS total_imports_value
    FROM
        trade T
    JOIN
        countries C
        ON T.countryCode = C.countryCode
    JOIN
        regions R
        ON C.regionCode = R.regionCode
    WHERE
        T.recordYear = 2020 AND
        T.seriesID = 11
    GROUP BY
        R.region
    ORDER BY
        R.region;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def exports_by_regions():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        R.region,
        SUM(T.val) AS total_exports_value
    FROM
        trade T
    JOIN
        countries C
        ON T.countryCode = C.countryCode
    JOIN
        regions R
        ON C.regionCode = R.regionCode
    WHERE
        T.recordYear = 2020 AND
        T.seriesID = 12
    GROUP BY
        R.region
    ORDER BY
        R.region;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def top5_and_bot5_balance():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
	C.country,
	T.val
FROM
	trade T
JOIN
	countries C
	ON T.countryCode = C.countryCode
INNER JOIN
	((SELECT
		T.val
	FROM
		trade T
	WHERE
		T.recordYear = 2020 AND
		T.seriesID = 13
	ORDER BY
		T.val DESC
	LIMIT 5)
	UNION ALL
	(SELECT
		T.val
	FROM
		trade T
	WHERE
		T.recordYear = 2020 AND
		T.seriesID = 13
	ORDER BY
		T.val ASC
	LIMIT 5)) AS T2
	ON T.val = T2.val
	ORDER BY T.val ASC;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def top10_imports():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        C.country,
        T.val
    FROM
        trade T
    JOIN
        countries C
        ON T.countryCode = C.countryCode
    WHERE
        T.recordYear = 2020 AND
        T.seriesID = 11
    ORDER BY
        T.val DESC
    LIMIT 10;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def top10_exports():
    cursor = connection.cursor(dictionary=True)
    
    # Execute the query
    query = '''
    SELECT
        C.country,
        T.val
    FROM
        trade T
    JOIN
        countries C
        ON T.countryCode = C.countryCode
    WHERE
        T.recordYear = 2020 AND
        T.seriesID = 12
    ORDER BY
        T.val DESC
    LIMIT 10;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

@charts_bp.route('/charts')
@login_required
def charts():
    total_emission_results = total_emission()
    avg_internet_results = avg_internet()
    total_trade_results = total_trade()

    # 1) PLOT EMISSION BY REGIONS RESULTS
    region_results = emission_by_regions()

    # Process the results for the pie chart
    regions = [row["region"] for row in region_results]
    emissions = [row["Total_CO2_Emission"] for row in region_results]

    #colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(regions)))
    colors = ["#DDDAD6", "#5DD4F0", "#006EB5", "#02A38A", "#757AF0"]
    # Create a pieplot
    plt.figure(figsize=(11, 11))
    #plt.pie(emissions, labels=regions, colors=colors, wedgeprops = { 'linewidth' : 3, 'edgecolor' : 'white' })
    plt.pie(emissions, labels=regions, colors=colors)

    # add a circle at the center to transform it in a donut chart
    my_circle=plt.Circle( (0,0), 0.7, color='white')
    p=plt.gcf()
    p.gca().add_artist(my_circle)

    # Save the pie chart to a bytes buffer
    img_pie = io.BytesIO()
    plt.savefig(img_pie, format='png', bbox_inches='tight')
    img_pie.seek(0)
    plt.close()

    # Encode the pie chart image to base64 string
    plot_pie_url = base64.b64encode(img_pie.getvalue()).decode('utf8')

    # 2) PLOT EMISSION BY REGIONS OVER YEARS RESULTS
    region_years_results = emission_by_regions_over_years()

    # Process the results for the pie chart
    regions = [row["region"] for row in region_years_results]
    regions = np.unique(regions)
    years = [row["recordYear"] for row in region_years_results]
    years = years[:6]
    emissions = [row["Total_CO2_Emission"] for row in region_years_results]
    emi = np.array_split(emissions, 5)

    # Basic stacked area chart.
    fig, ax = plt.subplots(figsize=(12,7))
    ax.stackplot(years,emi[0], emi[1], emi[2], emi[3], emi[4], labels=regions, colors=colors)

    # Make legend
    # Make room on top now
    fig.subplots_adjust(top=0.8)
    ax.legend(
        loc="lower center", # "upper center" puts it below the line
        ncol=5,
        bbox_to_anchor=(0.5, 0.8),
        bbox_transform=fig.transFigure 
    )

    # Save the pie chart to a bytes buffer
    img_pie = io.BytesIO()
    plt.savefig(img_pie, format='png', bbox_inches='tight')
    img_pie.seek(0)
    plt.close()

    # Encode the pie chart image to base64 string
    plot_stack_url = base64.b64encode(img_pie.getvalue()).decode('utf8')

    # 3) PLOT TOP 10 EMISSION BY COUNTRIES
    top10_emission_results = top10_emission_by_countries()
    
    # Process the results for the bar chart
    countries = [row["country"] for row in top10_emission_results]
    emissions_countries = [row["val"] for row in top10_emission_results]

    # Colors
    colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.3, 10))

    # compute circle positions
    circles = circlify.circlify(
        emissions_countries,
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    # reverse the order of the circles to match the order of data
    circles = circles[::-1]

    # Create just a figure and only one subplot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Remove axes
    ax.axis('off')

    # Find axis boundaries
    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r,
        )
        for circle in circles
    )
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # print circles
    for circle, country, color in zip(circles, countries, colors):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.8, linewidth=2, color=color))
        plt.annotate(
            country,
            (x, y),
            va='center',
            ha='center',
            color="white"
        )

    # Save the bar chart to a bytes buffer
    img_bar = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_bar, format='png', bbox_inches='tight')
    img_bar.seek(0)
    plt.close()

    # Encode the bar chart image to base64 string
    plot_circle1_url = base64.b64encode(img_bar.getvalue()).decode('utf8')


    # 4) PLOT TOP 10 EMISSION PER CAPITA BY COUNTRIES
    top10_emission_per_capita_results = top10_emission_per_capita_by_countries()
    
    # Process the results for the bar chart
    countries = [row["country"] for row in top10_emission_per_capita_results]
    emissions_countries = [row["val"] for row in top10_emission_per_capita_results]

    # Colors
    colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.5, 10))

    # compute circle positions
    circles = circlify.circlify(
        emissions_countries,
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    # reverse the order of the circles to match the order of data
    circles = circles[::-1]

    # Create just a figure and only one subplot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Remove axes
    ax.axis('off')

    # Find axis boundaries
    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r,
        )
        for circle in circles
    )
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # print circles
    for circle, country, color in zip(circles, countries, colors):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.8, linewidth=2, color=color))
        plt.annotate(
            country,
            (x, y),
            va='center',
            ha='center',
            color="white"
        )

    # Save the bar chart to a bytes buffer
    img_bar = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_bar, format='png', bbox_inches='tight')
    img_bar.seek(0)
    plt.close()

    # Encode the bar chart image to base64 string
    plot_circle2_url = base64.b64encode(img_bar.getvalue()).decode('utf8')

    # ------------------------------------------------------------------------
    ### INTERNET USAGE
    # ------------------------------------------------------------------------
    # 5) PLOT INTERNET BY REGIONS RESULTS
    region_results = internet_by_regions()

    # Process the results for the pie chart
    regions = [row["region"] for row in region_results]
    emissions = [row["avg_internet_usage"] for row in region_results]

    #colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(regions)))
    colors = ["#DDDAD6", "#5DD4F0", "#006EB5", "#02A38A", "#757AF0"]
    # Create a barplot
    fig, ax = plt.subplots(figsize=(11, 11))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    #ax.get_yaxis().set_ticks([])

    #plt.pie(emissions, labels=regions, colors=colors, wedgeprops = { 'linewidth' : 3, 'edgecolor' : 'white' })
    plt.bar(regions, emissions, color=colors)

    # Save the chart to a bytes buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()

    # Encode the pie chart image to base64 string
    plot_internet_bar_url = base64.b64encode(img.getvalue()).decode('utf8')

    # 6) PLOT INTERNET BY REGIONS OVER YEARS RESULTS

    region_years_results = internet_by_regions_over_years()

    # Process the results for the chart
    regions = [row["region"] for row in region_years_results]
    regions = np.unique(regions)
    years = [row["recordYear"] for row in region_years_results]
    years = years[:6]
    emissions = [row["avg_internet_usage"] for row in region_years_results]
    emi = np.array_split(emissions, 5)

    #colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(regions)))
    colors = ["#DDDAD6", "#5DD4F0", "#006EB5", "#02A38A", "#757AF0"]
    barWidth = 0.15

    # Bar positions
    r = np.arange(len(emi[0]))
    r2 = r + barWidth
    r3 = r2 + barWidth
    r4 = r3 + barWidth
    r5 = r4 + barWidth

    # Create a grouped barplot
    fig, ax = plt.subplots(figsize=(12,7))
    ax.bar(r, emi[0], color=colors[0], width=barWidth, edgecolor='white', label=regions[0])
    ax.bar(r2, emi[1], color=colors[1], width=barWidth, edgecolor='white', label=regions[1])
    ax.bar(r3, emi[2], color=colors[2], width=barWidth, edgecolor='white', label=regions[2])
    ax.bar(r4, emi[3], color=colors[3], width=barWidth, edgecolor='white', label=regions[3])
    ax.bar(r5, emi[4], color=colors[4], width=barWidth, edgecolor='white', label=regions[4])

    # Xticks
    ax.set_xticks(r + 2*barWidth)
    ax.set_xticklabels(years)

    # Make legend
    # Make room on top now
    fig.subplots_adjust(top=0.8)
    ax.legend(
        loc="lower center", # "upper center" puts it below the line
        ncol=5,
        bbox_to_anchor=(0.5, 0.8),
        bbox_transform=fig.transFigure 
    )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    #ax.get_yaxis().set_ticks([])

    # Save the chart to a bytes buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()

    # Encode the chart image to base64 string
    plot_internet_grouped_bar_url = base64.b64encode(img.getvalue()).decode('utf8')

    # 7) PLOT ALL INTERNET DATA
    internet_results = internet_all_data()
    
    # Process the results for the bar chart
    countries = [row["country"] for row in internet_results]
    usage = [row["val"] for row in internet_results]
    print(type(usage[0]))

    # set figure size
    plt.figure(figsize=(18,9))

    # plot polar axis
    ax = plt.subplot(111, polar=True)

    # remove grid
    plt.axis('off')

    # Set the coordinates limits
    upperLimit = 100
    lowerLimit = 30

    # Compute max and min in the dataset
    max2 = max(usage)

    # Let's compute heights: they are a conversion of each item value in those new coordinates
    # In our example, 0 in the dataset will be converted to the lowerLimit (10)
    # The maximum will be converted to the upperLimit (100)
    slope = (max2 - lowerLimit) / max2
    usage = np.array(usage)
    heights = slope * usage + lowerLimit

    # Compute the width of each bar. In total we have 2*Pi = 360°
    width = 2*np.pi / len(countries)

    # Compute the angle each bar is centered on:
    indexes = list(range(1, len(countries)+1))
    angles = [element * width for element in indexes]
    angles

    # Draw bars
    bars = ax.bar(
        x=angles, 
        height=heights, 
        width=width, 
        bottom=lowerLimit,
        linewidth=2, 
        edgecolor="white")
    
    # little space between the bar and the label
    labelPadding = 4

    countries = np.array(countries)
    # Add labels
    for bar, angle, height, label in zip(bars,angles, heights, countries):

        # Labels are rotated. Rotation must be specified in degrees :(
        rotation = np.rad2deg(angle)

        # Flip some labels upside down
        alignment = ""
        if angle >= np.pi/2 and angle < 3*np.pi/2:
            alignment = "right"
            rotation = rotation + 180
        else: 
            alignment = "left"

        # Finally add the labels
        ax.text(
            x=angle, 
            y=lowerLimit + bar.get_height() + labelPadding, 
            s=label, 
            ha=alignment, 
            va='center', 
            rotation=rotation, 
            rotation_mode="anchor",
            size="x-small") 
    
    # Save the chart to a bytes buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()

    # Encode the chart image to base64 string
    plot_internet_circular_bar_url = base64.b64encode(img.getvalue()).decode('utf8')

    # ------------------------------------------------------------------------
    ### IMPORTS/EXPORTS/TRADE
    # ------------------------------------------------------------------------
    # 8) Plot total imports & exports by regions
    imports_results = imports_by_regions()

    # Process the results for the pie chart
    regions = [row["region"] for row in imports_results]
    imports = [row["total_imports_value"] for row in imports_results]

    #colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(regions)))
    colors = ["#DDDAD6", "#5DD4F0", "#006EB5", "#02A38A", "#757AF0"]

    # Create the imports pieplot on the left
    plt.figure(figsize=(16,8))
    plt.subplot(1, 2, 1)
    #plt.pie(emissions, labels=regions, colors=colors, wedgeprops = { 'linewidth' : 3, 'edgecolor' : 'white' })
    plt.pie(imports, labels=regions, colors=colors)

    # add a circle at the center to transform it in a donut chart
    my_circle=plt.Circle( (0,0), 0.7, color='white')
    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.title("Imports")

    exports_results = exports_by_regions()
    regions = [row["region"] for row in exports_results]
    exports = [row["total_exports_value"] for row in exports_results]

    # Create the exports pieplot on the right
    plt.subplot(1, 2, 2)
    #plt.pie(emissions, labels=regions, colors=colors, wedgeprops = { 'linewidth' : 3, 'edgecolor' : 'white' })
    plt.pie(exports, labels=regions, colors=colors)
    plt.title("Exports")

    # add a circle at the center to transform it in a donut chart
    my_circle=plt.Circle( (0,0), 0.7, color='white')
    p=plt.gcf()
    p.gca().add_artist(my_circle)

    # Save the pie chart to a bytes buffer
    img_pie = io.BytesIO()
    plt.savefig(img_pie, format='png', bbox_inches='tight')
    img_pie.seek(0)
    plt.close()

    # Encode the pie chart image to base64 string
    plot_trade_pie_url = base64.b64encode(img_pie.getvalue()).decode('utf8')

    # 10) PLOT TOP 10 IMPORTS BY COUNTRIES
    top10_imports_results = top10_imports()
    
    # Process the results for the bar chart
    countries = [row["country"] for row in top10_imports_results]
    imports_countries = [row["val"] for row in top10_imports_results]

    # Colors
    colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.3, 10))

    # compute circle positions
    circles = circlify.circlify(
        imports_countries,
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    # reverse the order of the circles to match the order of data
    circles = circles[::-1]

    # Create just a figure and only one subplot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Remove axes
    ax.axis('off')

    # Find axis boundaries
    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r,
        )
        for circle in circles
    )
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # print circles
    for circle, country, color in zip(circles, countries, colors):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.8, linewidth=2, color=color))
        plt.annotate(
            country,
            (x, y),
            va='center',
            ha='center',
            color="white"
        )

    # Save the bar chart to a bytes buffer
    img_bar = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_bar, format='png', bbox_inches='tight')
    img_bar.seek(0)
    plt.close()

    # Encode the bar chart image to base64 string
    plot_trade_circle1_url = base64.b64encode(img_bar.getvalue()).decode('utf8')

    # 11) PLOT TOP 10 EXPORTS BY COUNTRIES
    top10_exports_results = top10_exports()
    
    # Process the results for the bar chart
    countries = [row["country"] for row in top10_exports_results]
    exports_countries = [row["val"] for row in top10_exports_results]

    # Colors
    colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.3, 10))

    # compute circle positions
    circles = circlify.circlify(
        exports_countries,
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    # reverse the order of the circles to match the order of data
    circles = circles[::-1]

    # Create just a figure and only one subplot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Remove axes
    ax.axis('off')

    # Find axis boundaries
    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r,
        )
        for circle in circles
    )
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # print circles
    for circle, country, color in zip(circles, countries, colors):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.8, linewidth=2, color=color))
        plt.annotate(
            country,
            (x, y),
            va='center',
            ha='center',
            color="white"
        )

    # Save the bar chart to a bytes buffer
    img_bar = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_bar, format='png', bbox_inches='tight')
    img_bar.seek(0)
    plt.close()

    # Encode the bar chart image to base64 string
    plot_trade_circle2_url = base64.b64encode(img_bar.getvalue()).decode('utf8')

    # 12) PLOT TOP 5 AND BOT 5 BALANCE BY COUNTRIES
    balance_results = top5_and_bot5_balance()
    
    # Process the results for the bar chart
    countries = [row["country"] for row in balance_results]
    balance = [row["val"] for row in balance_results]

    # Colors
    colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.3, 2))

    # Plotting
    fig, ax = plt.subplots(figsize=(12,6))
    plt.barh(y=countries[:5], width=balance[:5], color=colors[1])
    plt.barh(y=countries[5:], width=balance[5:], color=colors[0])

    # Save the bar chart to a bytes buffer
    img_bar = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_bar, format='png', bbox_inches='tight')
    img_bar.seek(0)
    plt.close()

    # Encode the bar chart image to base64 string
    plot_trade_barh_url = base64.b64encode(img_bar.getvalue()).decode('utf8')

    # Render the template with both images
    return render_template('charts.html', emission=total_emission_results, internet = avg_internet_results, trade = total_trade_results,
                           plot_pie_url=plot_pie_url, plot_stack_url=plot_stack_url, plot_circle1_url=plot_circle1_url, plot_circle2_url=plot_circle2_url,
                           plot_internet_bar_url=plot_internet_bar_url, plot_internet_grouped_bar_url=plot_internet_grouped_bar_url, plot_internet_circular_bar_url=plot_internet_circular_bar_url,
                           plot_trade_pie_url=plot_trade_pie_url, plot_trade_circle1_url=plot_trade_circle1_url, plot_trade_circle2_url=plot_trade_circle2_url,
                           plot_trade_barh_url=plot_trade_barh_url)

