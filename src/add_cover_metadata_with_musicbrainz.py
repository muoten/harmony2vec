import requests
import os
import re
import json
import pandas as pd
from utils.parse_config import config
from bs4 import BeautifulSoup
import time

SECONDS_TO_SLEEP = config['SECONDS_TO_SLEEP']
# use musicbrainz api to identify cover versions of a song that also contain video identifiers
USER_AGENT = config['USER_AGENT']
headers = {
		'User-Agent': USER_AGENT
}

def get_mbid_by_title(title):
	mbid = None
	# add user agent to the request	
	
	response = requests.get(f"https://musicbrainz.org/ws/2/work/?query=work:{title}&fmt=json", headers=headers)
	works = response.json()['works']
	if len(works) > 0 and works[0]['score'] == 100:
		mbid = works[0]['id']
	return mbid
 

def get_url_id_by_youtube_url(youtube_url):
	time.sleep(SECONDS_TO_SLEEP)
	url = f"https://musicbrainz.org/ws/2/url?resource={youtube_url}&fmt=json"
	response = requests.get(url, headers=headers)
	return response.json()['id']

def get_available_videos_by_mbid(mbid):
	response = requests.get(f"https://musicbrainz.org/ws/2/work/?query=mbid:{mbid}&fmt=json", headers=headers)
	print(response.json())
	relations = response.json()['works'][0]['relations']
	relations = [relation for relation in relations if 'recording' in relation and relation["recording"]["video"] is not None]
	return relations

def get_available_recordings_by_mbid(mbid):
	time.sleep(SECONDS_TO_SLEEP)
	response = requests.get(f"https://musicbrainz.org/ws/2/work/?query=mbid:{mbid}&fmt=json", headers=headers)
	relations = response.json()['works'][0]['relations']
	return relations

def get_first_mbid_by_relations(relations):
	relations = [relation for relation in relations if 'recording' in relation and relation["recording"]["video"] is not None]
	return relations[0]['recording']['id']


def get_metadata_by_recording_mbid(mbid):
	try:
		time.sleep(SECONDS_TO_SLEEP)
		url = f"https://musicbrainz.org/ws/2/recording/{mbid}?inc=artist-credits+url-rels&fmt=json"
		print(url)
		response = requests.get(url, headers=headers)
		print(response.json())

		if 'relations' not in response.json() or len(response.json()['relations']) == 0:
			raise Exception(f"relations not found or empty for recording {mbid}")
		youtube_url = [relation['url']['resource'] for relation in response.json()['relations'] if 'youtube' in relation['url']['resource']][0]
		youtube_id = youtube_url.split('v=')[1]

		# get the artist name from the recording
		artist_name = response.json()['artist-credit'][0]['artist']['name']
		# encode the artist name in ascii
		artist_name = artist_name.encode('ascii', 'ignore').decode('ascii')
	
		# get the title from the recording
		title = response.json()['title']
		return youtube_id, artist_name, title
	except Exception as e:
		print(e)
		return None, None, None

def get_entry_in_full_txt_by_youtube_id(youtube_id):
	command = f"grep {youtube_id} ~/youtube2wav16k_dataset/full.txt"
	os.system(command)
	entry = os.popen(command).read()
	return entry


def get_work_id_by_title(title):
	response = requests.get(f"https://musicbrainz.org/ws/2/work/?query=title:{title}&fmt=json", headers=headers)
	return response.json()['works'][0]['id']


def get_work_id_and_iswcs_by_mbid(mbid):
	response = requests.get(f"https://musicbrainz.org/ws/2/recording/{mbid}?fmt=json&inc=work-rels", headers=headers)
	work_id = response.json()['relations'][0]['work']['id']
	iswcs = response.json()['relations'][0]['work']['iswcs'][0]
	return work_id, iswcs


def get_metadata_by_title(title):
	mbid = get_mbid_by_title(title)
	relations = get_available_videos_by_mbid(mbid)
	recording_id = get_first_mbid_by_relations(relations)
	youtube_id, artist_name, title = get_metadata_by_recording_mbid(recording_id)
	return youtube_id, artist_name, title


def get_recording_mbid_by_url_id(youtube_url):
	mylinks = []
	time.sleep(SECONDS_TO_SLEEP)
	response = requests.get(youtube_url, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		soup = BeautifulSoup(response.text, 'html.parser')

	# select the link that has class "wrap-anywhere" 
	# and is after tag span with title "This recording is a video" or "recordinglink"
	video_span = soup.find('span', title='This recording is a video')
	if not video_span:
		video_span = soup.find('span', class_='recordinglink')
	
	# Get the next wrap-anywhere link after this span
	if video_span:
		next_link = video_span.find_next('a', class_='wrap-anywhere')
		if next_link:
			mylinks = [next_link]
	
	recording_link = [link for link in mylinks if 'wrap-anywhere' in link.get('class', [])][0]

	# get the href from the recording_link
	recording_id = recording_link.get('href')
	recording_id = recording_id.split('/')[2]
	return recording_id


def get_metadata_cover_by_work_id_and_mbid_original(work_id, mbid_original):
	versions = get_available_recordings_by_mbid(work_id)
	
	array_mbid_original = [version for version in versions if 'recording' in version and version['recording']['id'] == mbid_original]

	if len(array_mbid_original) > 0:
		versions = [relation for relation in versions if 'recording' in relation and relation["recording"]["video"] is not None]
		print("versions", versions)
		
		array_mbid_other = [version for version in versions if 'recording' in version and version['recording']['id'] != mbid_original]

		if len(array_mbid_other) == 0:
			print("work_id was identified but no other versions were found")
			return None, None, None
		for i, item_mbid_other in enumerate(array_mbid_other):
			mbid_other = item_mbid_other['recording']['id']
			print("mbid_other", mbid_other)
			youtube_id, artist_name, title = get_metadata_by_recording_mbid(mbid_other)
			if youtube_id is not None:
				print("youtube_id", youtube_id)
				print("artist_name", artist_name)
				print("title", title)
				return youtube_id, artist_name, title
		return None, None, None
	else:
		print(f"cover metadata not found for work_id {work_id} and mbid_original {mbid_original}")
		return None, None, None


def get_recording_mbid_by_youtube_id(youtube_id):
	youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
	try:
		url_id_original = get_url_id_by_youtube_url(youtube_url)
		print("url_id_original:", url_id_original)
		my_url = f"https://musicbrainz.org/url/{url_id_original}"
		mbid_original = get_recording_mbid_by_url_id(my_url)
		return mbid_original
	except Exception as e:
		print(e)
		return None


if __name__ == "__main__":

	#N = 249
	N = 830
	iswcs = None
	metadata_yt_output_file = config['METADATA_YT_OUTPUT_FILE']
	df = pd.read_csv(metadata_yt_output_file, sep='\t')

	print(df.iloc[N])
	my_song = df.iloc[N].song
	my_youtube_id = df.iloc[N].youtube_id

	try:
		mbid_original = get_recording_mbid_by_youtube_id(my_youtube_id)
		if mbid_original is None:
			print(f"youtube_id {my_youtube_id} not found in musicbrainz")
			exit()
		print("mbid_original:", mbid_original)
		
		work_id, iswcs = get_work_id_and_iswcs_by_mbid(mbid_original)
		print("work_id:", work_id)
		print("iswcs:", iswcs)

		youtube_id, artist_name, title = get_metadata_cover_by_work_id_and_mbid_original(work_id,mbid_original)
		print(youtube_id, artist_name, title)
	except Exception as e:
		print(e)
		mbid_original = None
		youtube_id = None
	
	# if youtube_id is not None or iswcs is not None, then we can update the csv file
	if youtube_id is not None or iswcs is not None:

		str_entry = get_entry_in_full_txt_by_youtube_id(my_youtube_id)

		dict_entry = json.loads(str_entry)
		work_id = dict_entry['work_id']

		old_work_id = df.iloc[N].work_id
		if not pd.isna(old_work_id):
			print("old_work_id was found in full txt file:", old_work_id)

			# replace all occurences of old_work_id with work_id
			df.loc[df['work_id'] == old_work_id, 'work_id'] = work_id
		else:
			df.loc[N, 'work_id'] = work_id

		if iswcs is not None:
			df.loc[N, 'iswcs'] = iswcs

		if youtube_id is not None:
			print(f"Inserting row for youtube_id {youtube_id} at position {N+1}")
			# Insert one row to the dataframe just after N with an empty row
			df = pd.concat([df.iloc[:N+1], pd.DataFrame([{}], columns=df.columns), df.iloc[N+1:]], ignore_index=True)

			# containing output from get_metadata_cover_by_work_id_and_mbid_original 
			df.loc[N+1, 'youtube_id'] = youtube_id
			df.loc[N+1, 'artist'] = artist_name.lower()
			df.loc[N+1, 'song'] = title.lower()
			df.loc[N+1, 'work_id'] = work_id
			df.loc[N+1, 'iswcs'] = iswcs
			df.loc[N+1, 'tempo'] = -1

		# save the dataframe to the csv file
		df.to_csv(metadata_yt_output_file, sep='\t', index=False)
