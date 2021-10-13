@pyscript_compile
def parse_weatheri(url = 'https://www.weatheri.co.kr/main01_2.php?select=9&select2=11H20201'):
    import requests, re
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    b = soup.select('td > font > b')
    return (re.search('\d+/\d+', b[1].get_text())[0],
        re.search('\d+', b[2].get_text())[0],
        re.search('\d+', b[3].get_text())[0],
        re.search('\d+', b[5].get_text())[0],
        re.search('\d+', b[6].get_text())[0],
        re.search('\d+', b[8].get_text())[0],
        re.search('\d+', b[9].get_text())[0])

@time_trigger('cron(0,1,2,4,8,16,32 0 * * *)')
def weatheri_forecast(url = 'https://www.weatheri.co.kr/main01_2.php?select=9&select2=11H20201'):
    from datetime import date
    try:
        last_update = state.get('sensor.weatheri_last_update')
    except:
        last_update = ''
    today = date.today().strftime('%-m/%-d')
    if last_update == today:
        log.debug('Already updated today')
    else:
        try:
            data = task.executor(parse_weatheri, url=url)
        except:
            log.warning('Weatheri parse error.')
        weatheri_date = data[0]
        if today != weatheri_date:
            log.info('Weatheri not updated yet')
        else:
            try:
                state.set('sensor.weatheri_today_high', data[1])
                state.set('sensor.weatheri_today_low', data[2])
                state.set('sensor.weatheri_tomorrow_high', data[3])
                state.set('sensor.weatheri_tomorrow_low', data[4])
                state.set('sensor.weatheri_overmorrow_high', data[5])
                state.set('sensor.weatheri_overmorrow_low', data[6])
                state.set('sensor.weatheri_last_update', data[0])
            except:
                log.warning('Weatheri state set error.')


@service
def weatheri_forecast_reset():
    state.delete('sensor.weatheri_today_high')
    state.delete('sensor.weatheri_today_low')
    state.delete('sensor.weatheri_tomorrow_high')
    state.delete('sensor.weatheri_tomorrow_low')
    state.delete('sensor.weatheri_overmorrow_high')
    state.delete('sensor.weatheri_overmorrow_low')
    state.delete('sensor.weatheri_last_update')
