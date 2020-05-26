import sqlite3 as lite
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from scipy.signal import savgol_filter

conn = None

try:
    record_date = []
    pressure_pa = []
    temperature_celcius = []
    
    conn = lite.connect('weather_info.db')
    curs = conn.cursor()

    curs.execute("SELECT * FROM weather_data")

    conn.commit()

    data = curs.fetchall()
    
    for row in data:
        record_date.append(parser.parse(row[0]))
        pressure_pa.append(row[1])
        temperature_celcius.append(row[2])

    # smoothing
    pressure_pa_smooth = savgol_filter(pressure_pa, 51, 3)
    temp_c_smooth = savgol_filter(temperature_celcius, 51, 3)
    
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Pressure Pa', color=color)
    ax1.plot(record_date, pressure_pa_smooth, color=color, label='Pressure Pa')
    # ax1.plot(record_date, pressure_pa_smooth)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel(r'Temperature $\degree$C', color=color)
    ax2.plot(record_date, temp_c_smooth, color=color, label='Temperature $\degree$C')
    # ax2.plot(record_date, temp_c_smooth)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    fig.autofmt_xdate()
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    ax2.legend(lines1 + lines2, labels1 + labels2)

    plt.show()
    
    #plt.plot_date(record_date, pressure_pa, '-')
    #plt.xlabel('Time')
    #plt.ylabel('Pressure PA')
    #plt.show()


except lite.Error, e:
    print "Error {}:".format(e.args[0])
    sys.exit(1)

finally:
    if conn:
        conn.close()
