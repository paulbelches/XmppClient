from twitterscraper import query_tweets
import datetime as dt
import pandas as pd

begin_date = dt.date(2019, 4, 15)
end_date = dt.date(2019, 4, 18)

meses = {
    # mes, Fechainicio, Fechafin
    0: ['enero', dt.date(2020, 1, 1), dt.date(2020, 1, 31)],
    1: ['febrero', dt.date(2020, 2, 1), dt.date(2020, 2, 29)],
    2: ['marzo', dt.date(2020, 3, 1), dt.date(2020, 3, 31)],
    3: ['abril', dt.date(2020, 4, 1), dt.date(2020, 4, 30)],
    4: ['mayo', dt.date(2020, 5, 1), dt.date(2020, 5, 31)],
    5: ['junio', dt.date(2020, 6, 1), dt.date(2020, 6, 30)],
    6: ['julio', dt.date(2020, 7, 1), dt.date(2020, 7, 31)],
    7: ['agosto', dt.date(2020, 8, 1), dt.date(2020, 8, 31)],
}

limit = 1000
lang = 'es'

i = 7 ##Aqui iria un for
tweets = query_tweets("giammattei", begindate=meses[i][1],
                      enddate=meses[i][2], limit=limit, lang=lang)
df = pd.DataFrame(t.__dict__ for t in tweets)
df.to_csv('files/'+str(meses[i][0])+'.csv')