@time_trigger
def initiate_weatheri():
    state.persist('pyscript.weatheri_last_update') # survive HASS restarts
    attr = state.get_attr('pyscript.weatheri_last_update')
    if attr is None:
        # if no value, fetch new values
        weatheri_forecast()
        attr = state.get_attr('pyscript.weatheri_last_update')
    weatheri_set_states(attr)

def weatheri_set_states(attr):
    if len(attr) > 0:
        for key, val in attr.items():
            state.set('sensor.weatheri_' + key, val)
    else:
        log.error('Weatheri attributes is empty.')

@pyscript_compile
def parse_weatheri(url = 'https://www.weatheri.co.kr/main01_2.php?select=9&select2=11H20201'):
    import requests, re
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    b = soup.select('td > font > b')
    try:
        webpage_date = re.search('\d+/\d+', b[1].get_text())[0]
        attr = {
            'today_high': re.search('\d+', b[2].get_text())[0],
            'today_low': re.search('\d+', b[3].get_text())[0],
            'tomorrow_high': re.search('\d+', b[5].get_text())[0],
            'tomorrow_low': re.search('\d+', b[6].get_text())[0],
            'overmorrow_high': re.search('\d+', b[8].get_text())[0],
            'overmorrow_low': re.search('\d+', b[9].get_text())[0]
        }
    except:
        log.error('Weatheri information incomplete.')
        return '', {}
    return webpage_date, attr

@time_trigger('cron(0,1,2,4,8,16,32 0 * * *)') 
def weatheri_forecast(url = 'https://www.weatheri.co.kr/main01_2.php?select=9&select2=11H20201'):
    from datetime import date
    try:
        last_update = state.get('pyscript.weatheri_last_update')
    except:
        last_update = ''
    today = date.today().strftime('%-m/%-d')
    if last_update == today:
        log.debug('Weatheri already updated today.')
    else:
        try:
            webpage_date, attr = task.executor(parse_weatheri, url=url)
        except:
            log.error('Weatheri parse error.')
        if today != webpage_date:
            log.info('Weatheri not updated yet.')
        else:
            state.set('pyscript.weatheri_last_update', today, attr)
            weatheri_set_states(attr)

@service
def weatheri_forecast_reset():
    state.delete('pyscript.weatheri_last_update')
    state.delete('sensor.weatheri_today_high')
    state.delete('sensor.weatheri_today_low')
    state.delete('sensor.weatheri_tomorrow_high')
    state.delete('sensor.weatheri_tomorrow_low')
    state.delete('sensor.weatheri_overmorrow_high')
    state.delete('sensor.weatheri_overmorrow_low')
    log.info('Weatheri states have been deleted.')
    initiate_weatheri()
