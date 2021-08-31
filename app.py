from math import pi
import requests, json, re
import streamlit as st
import pandas as pd
from bokeh.plotting import figure, show

@st.cache
def yahoo(symb,t,dt=None):
    with requests.session() as s:
        return json.loads(s.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/" + symb +
            "?region=US&lang=en-US&includePrePost=false" +
            ("&interval="+dt if not (dt is None) else '') +
            "&useYfid=true&range=" + t +
            "&corsDomain=finance.yahoo.com&.tsrc=finance'",
            headers = {
                'Connection': 'keep-alive',
                'Expires': '-1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
            }).text)

units = {
    'm' : 1000*60,
    'd' : 1000*60*60*24,
    'wk': 1000*60*60*24*7,
    'mo': 1000*60*60*24*30,
    'y' : 1000*60*60*365
}

def main():
    st.title('Stocks')
    st.write('[TDI 12-Day program](https://app.thedataincubator.com/12day.html#day10)')
    st.write('Data from [Yahoo finance](https://finance.yahoo.com/)')
    st.write('Code on [GitHub](https://github.com/ivankp/tdi-stocks-streamlit-heroku)')

    # Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
    time_intervals = [
        ['1d','1m'], ['5d','5m'], ['15d','15m'],
        ['1mo','90m'], ['3mo','1d'], ['6mo','1d'],
        ['1y','1d'], ['2y','1d'], ['5y','1wk'], ['10y','1mo'],
        ['max','1mo']
    ]

    t,dt = time_intervals[st.select_slider('Time interval',
        value = 3,
        options = range(len(time_intervals)),
        format_func = lambda i: time_intervals[i][0]
    )]
    st.text(f'{t}/{dt}')

    symb = st.text_input('Symbol','^DJI')

    try:
        data = yahoo(symb,t,dt)
        # st.text(data)
        # print(data)
        result = data['chart']['result'][0]
        meta = result['meta']
        gmtoffset = meta['gmtoffset']
        try:
            df = pd.DataFrame({
                'timestamp': pd.to_datetime([
                    t+gmtoffset for t in result['timestamp']
                ],unit='s'),
                **result['indicators']['quote'][0]
            })
        except:
            st.text(f'Error: Missing or incomplete data')
            return
        else:
            st.write(df)
    except:
        try:
            st.text(f'Error: {data["chart"]["error"]["description"]}')
        except:
            st.text(f'Error: failed to process request')
        return

    with st.container():
        p = figure(
            x_axis_type='datetime',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            # plot_width=1000,
            title = symb)
        p.xaxis.major_label_orientation = pi/4
        p.grid.grid_line_alpha = 0.3

        inc = df.close > df.open
        dec = df.open > df.close
        n,u = re.match(r'(\d+)(.+)',dt).groups()
        w = int(n)*units[u]*0.75

        p.segment(df.timestamp, df.high, df.timestamp, df.low, color='black')
        p.vbar(df.timestamp[inc], w, df.open[inc], df.close[inc],
            fill_color="#007532", line_color=None)
        p.vbar(df.timestamp[dec], w, df.open[dec], df.close[dec],
            fill_color="#CE2A1D", line_color=None)

        st.bokeh_chart(p, use_container_width=True)
        # show(p)

if __name__ == "__main__":
    main()

