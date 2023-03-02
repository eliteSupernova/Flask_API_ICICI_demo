# import MySQL as MySQL
from statistics import mean

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import datetime
import pandas as pd
import pymysql
# from config import mysql
from flask import Flask, request, jsonify, send_file
from flaskext.mysql import MySQL
app=Flask(__name__)


mysql=MySQL()
app.config['MYSQL_DATABASE_USER']="root"
app.config['MYSQL_DATABASE_PASSWORD']="password"
app.config['MYSQL_DATABASE_DB']="icici_direct"
app.config['MYSQL_DATABASE_HOST']="localhost"
mysql.init_app(app)

def format_date(date,day):
    date_dt = datetime.datetime.strptime(date, "%Y%m%d")
    date_dt -= datetime.timedelta(days=day,hours=0,minutes=0,seconds=0)
    start_date=date_dt
    # print(start_date)
    # print(date_dt)
    return start_date


def to_csv(final_data,row,col):
    arr=np.array(final_data)
    table = arr.reshape(row,col)
    return table

def percentile(l1):
    arr=np.array(l1)
    percent=np.percentile(arr,95)
    return percent

# print(format_date('20221125',6))

@app.route('/dates/<string:end_date>/<int:day>', methods=['GET'])
def string_to_date(end_date,day):
    # return str(date)
    start_date = format_date(end_date,day-1)
    # new_end_date=datetime.datetime.strptime(start_date, "%Y%m%d")
    new_end_date=start_date+datetime.timedelta(hours=23, minutes=59, seconds=59)
    print(new_end_date)
    print(start_date)

    conn = mysql.connect()
    cur = conn.cursor()
    main_sql='select round(avg(Response_time),2) from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s AND %s;'
    sql = 'select distinct(Page_name) from icici_mobile_app_andriod_5min;'
    cur.execute(sql)
    pag_es = cur.fetchall()
    page=[i[0] for i in pag_es]
    data = []
    date=[]
    for i in page:
        # data = {}
        start_at=start_date
        end_at=new_end_date
        for j in range(day):
            vals=(i,start_at,end_at)
            date.append(start_at)
            start_at += datetime.timedelta(days=1)
            end_at += datetime.timedelta(days=1)
            # vals = (i, start_at, end_at)
            cur.execute(main_sql,vals)
            row=cur.fetchall()
            print(row)
            data.append(row)
    final_date=[]
    for i in date:
        if i not in final_date:
            final_date.append(i)
    new_final_date=[]
    for i in final_date:
        if i not in new_final_date:
            new_final_date.append(i.strftime('%d-%m-%Y'))
    print(new_final_date)
    table=['NULL' if i[0] is None else i[0] for i in data]
    print(table)
    new_data = to_csv(table,len(page),day)
    file=pd.DataFrame(new_data,index=page,columns=final_date)
    print(file)

    file.to_csv('C:\\Users\\1003647\\Desktop\\FLASK_API\\ICICI_csvfile\\'+str(start_date.date())+'_'+str(day)+'.csv')
    plt.figure(figsize=(20, 10))
    for i in page:
            plt.plot(new_final_date,file.loc[i], linewidth=2, label=i,marker='o')
    plt.legend()
    plt.ylabel('Values')
    plt.xlabel('Dates')
    plt.title('ICICI')
    plt.savefig('C:\\Users\\1003647\\Desktop\\FLASK_API\\ICICI_csvfile\\graph.png', dpi=1200)
    # plt.show()
    # print(file.loc['01_Login'])
    return send_file('C:\\Users\\1003647\\Desktop\\FLASK_API\\ICICI_csvfile\\graph.png')


@app.route('/new/stats/<string:end_date>/<int:day>', methods=['GET'])
def stats(end_date,day):
    start_date = format_date(end_date, day - 1)
    new_end_date = start_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
    conn = mysql.connect()
    cur = conn.cursor()
    sql = 'select distinct(Page_name) from icici_mobile_app_andriod_5min;'
    cur.execute(sql)
    pag_es = cur.fetchall()
    page = [i[0] for i in pag_es]
    new_page=[]
    main_data={}
    date = []
    min_data = []
    max_data = []
    avg_data = []
    percent=[]
    main_sql='select Response_time from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s AND %s;'

    start_at = start_date
    end_at = new_end_date
    for j in range(day):
        for i in page:
            vals=(i,start_at,end_at)
            date.append(str(start_at.date()))
            cur.execute(main_sql,vals)
            rows=(cur.fetchall())
            all_row=[i[0] for i in rows]

            print(i,all_row)
            if all_row[0] == []:
                min_data.append(0)
                max_data.append(0)
                avg_data.append(0)
                percent.append(0)
                print(all_row)
            else:
                min_data.append(round(min(all_row),2))
                max_data.append(round(max(all_row),2))
                avg_data.append(round(mean(all_row),2))
                percent.append(round(percentile(all_row),2))
                new_page.append(i)
        start_at += datetime.timedelta(days=1)
        end_at += datetime.timedelta(days=1)
    print(new_page)
    main_data['date']=date
    main_data['Page']=new_page
    main_data['Min_response']=min_data
    main_data['Max_response']=max_data
    main_data['AVG_Response']=avg_data
    main_data['95_percentile']=percent
    print(main_data)
    data=pd.DataFrame(main_data)
    # data.to_csv('C:\\Users\\1003647\\Desktop\\FLASK_API\\ICICI_csvfile\\'+str(start_date.date())+'_'+str(day)+'.csv',index=False)
    for i in data.iloc[:,[1,2,3,4,5]].values:
        print(i)

    # login=[i for i in data['page',]]
    # fig, ax = plt.subplots()
    # ax.set_xlabel('Date')
    # ax.set_ylabel('Response Time (s)')

    # Add a line for each page
    # ax.plot(*login_data, label='Login')
    # ax.plot(*watchlist_data, label='Watchlist')
    # ax.plot(*logout_data, label='Logout')
    #
    # # Add a legend
    # ax.legend()
    #
    # # Show the plot
    # plt.show()

    return '1'





@app.route('/stat/<string:end_date>/<int:day>', methods=['GET'])
def stat(end_date,day):
    start_date = format_date(end_date, day - 1)
    # new_end_date=datetime.datetime.strptime(start_date, "%Y%m%d")
    new_end_date = start_date + datetime.timedelta(hours=23, minutes=59, seconds=59)
    print(new_end_date)
    print(start_date)
    conn = mysql.connect()
    cur = conn.cursor()
    sql = 'select distinct(Page_name) from icici_mobile_app_andriod_5min;'
    cur.execute(sql)
    pag_es = cur.fetchall()
    page = [i[0] for i in pag_es]
    sql_per='select Response_time from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s and %s;'
    min_sql= 'select round(min(Response_time),2) AS "Min_Response" from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s and %s;'
    max_sql= 'select round(max(Response_time),2) AS "Min_Response" from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s and %s;'
    avg_sql = 'select round(avg(Response_time),2) AS "AVG_Response" from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s AND %s;'
    main_data={}
    date=[]
    min_data=[]
    max_data=[]
    avg_data=[]
    percent=[]
    percen_tile = []
    print(page)
    no_date=len(set(date))
    for x in range(day):
        for i in page:
            # percen_tile=[]
            start_at = start_date
            end_at = new_end_date
            for j in range(day):
                vals = (i, start_at, end_at)
                # start_at += datetime.timedelta(days=1)
                # end_at += datetime.timedelta(days=1)
                # vals = (i, start_at, end_at)
                date.append(str(start_at.date()))

                cur.execute(min_sql, vals)
                min_row = cur.fetchall()
                if min_row[0][0]==None:
                    min_data.append(0)
                else:
                    min_data.append(min_row[0][0])
                cur.execute(max_sql,vals)
                max_row = cur.fetchall()
                if max_row[0][0]==None:
                    max_data.append(0)
                else:
                    max_data.append(max_row[0][0])
                # max_data.append(max_row[0][0])
                cur.execute(avg_sql,vals)
                avg_row = cur.fetchall()
                if avg_row[0][0] is None:
                    avg_data.append(0)
                else:
                    avg_data.append(avg_row[0][0])
                # avg_data.append(avg_row[0][0])
                cur.execute(sql_per,vals)
                per=cur.fetchall()
                # if per[0][0] is None:
                #     per.append(0)
                # else:
                #     per.append(per[0][0])
                for i in per:
                    if i[0] is None:
                        percent.append(0)
                    else:
                        percent.append(i[0])

                print(percent)
                x=np.array(percent)
                percen=np.percentile(x,95)
                # if percent is None:
                #     percen_tile.append(0)
                # else:
                #     percen_tile.append(round(percent, 2))
                percen_tile.append(round(percen,2))
            start_at += datetime.timedelta(days=1)
            end_at += datetime.timedelta(days=1)

        #
    print(min_data)
    print(date)
    print(max_data)
    print(avg_data)
    print(percen_tile)
    main_data['date']=date
    main_data['Page']=page
    main_data['Min_response']=min_data
    main_data['Max_Response']=max_data
    main_data['Avg_Response']=avg_data
    main_data['95_percentile']=percen_tile
    df=pd.DataFrame(main_data)
    print(df)
    page=df['Page']
    avg=df['Avg_Response']
    # col=df.columns.values
    # col_list=list(col)
    # col_list.pop(0)
    # print(col_list)
    # print(df.iloc[2:3,1:])
    x = ['Min_response', 'Max_Response', 'Avg_Response', '95_percentile']
    x_axis=np.arange(len(x))
    n=-0.25
    plt.figure(figsize=(20, 10))
    # x=['Min_response', 'Max_Response', 'Avg_Response', '95_percentile']
    # for i in range(0,len(page)):
    # sns.barplot(df)
    for i in range(len(page)):
        y=df.loc[i].values
        print(y)
        plot=plt.bar(x_axis+n,y[1:],width=0.25,label=y[0])

        n+=0.25
        plt.xticks(x_axis,x)
        for bar in plot.patches:
            plt.annotate(format(bar.get_height(), '.2f'),
             (bar.get_x() + bar.get_width() / 2,
              bar.get_height()), ha='center', va='center',
             size=10, xytext=(0, 8),
             textcoords='offset points')
    plt.legend()
    # plt.show()
    plt.savefig('C:\\Users\\1003647\\Desktop\\FLASK_API\\ICICI_csvfile\\graph_one.png')
    # for i in range(0,4):
        # plt.bar(df.iloc[i-1:i,1:],df['Page'],width=barWidth)
    # plt.xticks([r + barWidth for r in range(3)])
    # plt.show()
    return send_file('C:\\Users\\1003647\\Desktop\\FLASK_API\\ICICI_csvfile\\graph_one.png')

# @app.route('/<string:enddate>/<int:day>', methods=['GET'])
# def read(enddate,day):
#     start_date=format_date(enddate,day)
#     start_date=start_date+datetime.timedelta(hours=0,minutes=0,seconds=0)
#     # print(start_date)
#     end_date=datetime.datetime.strptime(enddate, "%Y%m%d")
#     +datetime.timedelta(hours=59, minutes=59, seconds=59)
#     sql='select round(avg(Response_time),2) from icici_mobile_app_andriod_5min where Page_name=%s and StartTime between %s and %s;'
#
#     return '1'


if __name__=="__main__":
    app.run(debug = True)