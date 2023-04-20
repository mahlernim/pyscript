import re
import requests
CHANNEL_ID = "1784656"

@pyscript_executor
def episode_info(episode_id=0, increment=0, sort="desc"):
    limit = abs(increment) * 2 + 1
    url = f'https://app-api6.podbbang.com/channels/{CHANNEL_ID}/episodes?offset=0&limit={limit}&sort={sort}&episode_id={episode_id}&focus_center=1'
    response = requests.get(url)
    response_dict = response.json()
    data = response_dict['data']
    extracted_data = []
    for d in data:
        title = d['title']
        match = re.search(r'^(\d+)', title)
        num = int(match.group(1)) if match else "번호없음"
        extracted_data.append({
            'id': d['id'],
            'title': title,
            'url': d['media']['url'],
            'num': num,
        })
    if increment <= 0:
        return extracted_data[-1]
    else:
        return extracted_data[0]

@service
def sunkim_play(increment=0):
    if state.get("input_boolean.sunkim_player") != "on":
        state.set("input_boolean.sunkim_player", "on")
        return
    episode_id = int(float(state.get("input_number.sunkim_episode_id")))
    episode = episode_info(episode_id, increment)
    if increment > 0 and episode_id == episode['id']:
        episode = episode_info(sort="asc")
    elif increment < 0 and episode_id == episode['id']:
        episode = episode_info(sort="desc")
    state.set("input_number.sunkim_episode_id", episode['id'])
    tts.google_translate_say(entity_id="media_player.bedroom_speaker", message=episode['num'], language="ko", cache=True)
    task.sleep(4)
    media_player.play_media(entity_id="media_player.bedroom_speaker", media_content_id=episode['url'], media_content_type="audio/mp3")
