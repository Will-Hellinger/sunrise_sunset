import os
import pygame
import numpy
import json
import glob
import PySimpleGUI as sg

from scraper import *


def clear_console():
	os.system(clear)


def find_nearest(array, value):
	for s in range(len(array)):
		if array[s] is None:
			array[s] = 0
	array = numpy.asarray(array)
	idx = (numpy.abs(array - value)).argmin()
	return array[idx]


def drawGraph(surface, pen_color, pen_width, spacer, screen_resolution, fill_color = 'BLACK'):
	surface.fill(fill_color)
	pygame.draw.line(surface, pen_color,[spacer, spacer], [spacer, (screen_resolution[0] - spacer)], int(pen_width / 10))
	pygame.draw.line(surface, pen_color,[spacer, (screen_resolution[0] - spacer)], [(screen_resolution[1] - spacer), (screen_resolution[0] - spacer)], int(pen_width / 10))
	for s in range(len(months)):
		pygame.draw.line(surface, pen_color,[((((screen_resolution[1] - spacer) - spacer) / int(len(months))) * (s+1)) + spacer, (((screen_resolution[0] - spacer)) - 5)], [((((screen_resolution[1] - spacer) - spacer) / int(len(months))) * (s + 1)) + spacer, (((screen_resolution[0] - spacer)) + 5)], (int(pen_width / 10)))
	#hours in a day
	for s in range(24):
		pygame.draw.line(surface, pen_color,[spacer - 5, ((((screen_resolution[0] - spacer) - spacer) / 24)*s) + spacer], [spacer + 5, ((((screen_resolution[0] - spacer) - spacer) / 24) * s) + spacer], (int(pen_width / 10)))
	pygame.display.flip()


screen_resolution = [500, 500]
#Dont edit this unless you know what you're doing
pen_width = 10
spacer = 10
pen_color = 'WHITE'
years = []
locations = []
days = []

colors = ['PURPLE', 'WHITE', 'ORANGE', 'BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE']

surface = pygame.display.set_mode([screen_resolution[1], screen_resolution[0]])
pygame.display.set_caption("Sunrise-Sunset Project")

drawGraph(surface, pen_color, pen_width, spacer, screen_resolution)


def load_layout():
	global years
	global locations
	global days
	
	files = glob.glob(f'.{subdirectory}data{subdirectory}months{subdirectory}*.json')
	years = []
	locations = []
	days = []

	for file in files:
		year = int(file.split('_')[1])
		location = str(file.split('_')[2]).replace('.json', '')

		if year not in years:
			years.append(year)
		if location not in locations:
			locations.append(location)

	for day in range(1, 32):
		days.append(day)
	
	layout = [[sg.Text('Background Color:'), sg.Combo(colors, default_value='BLACK', key='_BACKGROUND_COLOR_'), sg.Text('Line Color:'), sg.Combo(colors, default_value='WHITE', key='_LINE_COLOR_')],]
	
	if locations != []:
		layout.append([sg.Text('Location Selector:'), sg.Combo(locations, default_value=locations[0], key='_LOCATION_')])
	else:
		layout.append([sg.Text('Location Selector: NO OPTIONS')])
	
	for year in years:
		layout.append([sg.Text(f'{year} Sunrise Color:'), sg.Combo(colors, default_value=colors[0], key=f'_{year}_SUNRISE_COLOR_'), sg.Text(f'Sunset Color:'), sg.Combo(colors, default_value=colors[0], key=f'_{year}_SUNSET_COLOR_'), sg.Checkbox('Hide', default=False, key=f'_{year}_HIDE_'), sg.Text('', key=f'_{year}_EQUATION_')])

	lower_layout = [
		[sg.Text(f'Date:'), sg.Combo(days, days[0], key='_DATE_INPUT_')],
		[sg.Button('DISPLAY')],
		[sg.Text('Year Input:'), sg.Input(key='_YEAR_INPUT_'), sg.Text('City Input:'), sg.Input(key='_CITY_INPUT_'), sg.Text('Location Input:'), sg.Input(key='_LOCATION_INPUT_')],
		[sg.Button('SCRAPE')]
		]

	layout.extend(lower_layout)

	return layout


def check_daylight_savings(sunsets: list, index: int, date: int, previous_feedback: bool):
	try:
		if date >= 29 or date << 30:
			if int(sunsets[index - 2]) - int(sunsets[index]) >= 70:
				return False
			elif int(sunsets[index]) - int(sunsets[index - 2]) >= 70:
				return True
		else:
			if int(sunsets[index - 1]) - int(sunsets[index]) >= 60:
				return False
			elif int(sunsets[index]) - int(sunsets[index - 1]) >= 60:
				return True
	except:
		pass
	return previous_feedback


def get_highest_value(list: list):
	if len(list) == 0:
		return 0
	
	output = list[0]

	for item in list:
		if item is None:
			continue

		if item >= output:
			output = item
	return output


def get_lowest_value(list: list):
	if len(list) == 0:
		return 0
	
	output = list[0]
	
	for item in list:
		if item is None:
			continue

		if item <= output:
			output = item
	return output


def display(surface, screen_resolution, year: int, city: str, sunrise_color: str, sunset_color: str, date: int):
	sunsets = []
	sunrises = []
	file_location = f'.{subdirectory}data{subdirectory}months{subdirectory}'

	for month in months:
		filename = f'{abbreviate_month(month)}_{year}_{city}.json'

		with open(file_location + filename, mode='r', encoding='utf-8') as file:
			data = json.load(file)
			day = data.get(str(date))

			if day is None:
				sunrises.append(None)
				sunsets.append(None)
				continue

			sunrise = day.get('sunrise')
			sunset = day.get('sunset')

			sunrise = sunrise.replace(' am', '')
			sunrise = sunrise.split(':')
			sunrise = (int(sunrise[0]) * 60) + int(sunrise[1])

			sunset = sunset.replace(' pm', '')
			sunset = sunset.split(':')
			sunset = (int(sunset[0]) * 60) + int(sunset[1])

			sunrises.append(sunrise)
			sunsets.append(sunset)
	
	previous_feedback = False
	daylights = []
	for sunset in range(0, len(sunsets)):
		if previous_feedback == True and (check_daylight_savings(sunsets, sunset, date, previous_feedback)) == False:
			daylights.append(True)
			previous_feedback = False
			continue
		#delays by a day for leaving daylights savings, idk man, weather moment
		#breaks past day 20, need to investigate

		previous_feedback = (check_daylight_savings(sunsets, sunset, date, previous_feedback))
		daylights.append(previous_feedback)

	for sunset in range(0, len(sunsets)):
		if sunsets[sunset] is None:
			continue

		sunsets[sunset] += 660
		if daylights[sunset] == True:
			sunsets[sunset] -= 60
		
		pygame.draw.circle(surface, sunset_color, (((((screen_resolution[1] - spacer) - spacer)/int(len(months)))*(sunset+1))+spacer, (screen_resolution[0]-spacer)-((((screen_resolution[0]-spacer)-spacer)/24)*((sunsets[sunset])/60))), 3)

	for sunrise in range(0, len(sunrises)):
		if sunrises[sunrise] is None:
			continue

		if daylights[sunrise] == True:
			sunrises[sunrise] -= 60
		
		pygame.draw.circle(surface, sunrise_color, (((((screen_resolution[1]-spacer)-spacer)/int(len(months)))*(sunrise+1))+spacer, (screen_resolution[0]-spacer)-((((screen_resolution[0]-spacer)-spacer)/24)*((sunrises[sunrise])/60))), 3)

	pygame.display.flip()

	sunset_sin_equation = f'y={round((get_highest_value(sunsets)-get_lowest_value(sunsets))/2)}sin({round(360/12)}(x+{((sunsets.index(find_nearest(sunsets, ((get_highest_value(sunsets)+get_lowest_value(sunsets))/2))))+1)*-1}))+{round((get_highest_value(sunsets)+get_lowest_value(sunsets))/2)}'
	sunset_cos_equation = f'y={round((get_highest_value(sunsets)-get_lowest_value(sunsets))/2)}cos({round(360/12)}(x+{((sunsets.index(find_nearest(sunsets, ((get_highest_value(sunsets)+get_lowest_value(sunsets))/2))))+1)*-1})-90)+{round((get_highest_value(sunsets)+get_lowest_value(sunsets))/2)}'

	sunrise_sin_equation = f'y={round((get_highest_value(sunrises)-get_lowest_value(sunrises))/2)}sin({round(360/12)}(x+{((sunrises.index(find_nearest(sunrises, ((get_highest_value(sunrises)+get_lowest_value(sunrises))/2))))+1)*-1}))+{round((get_highest_value(sunrises)+get_lowest_value(sunrises))/2)}'
	sunrise_cos_equation = f'y={round((get_highest_value(sunrises)-get_lowest_value(sunrises))/2)}cos({round(360/12)}(x+{((sunrises.index(find_nearest(sunrises, ((get_highest_value(sunrises)+get_lowest_value(sunrises))/2))))+1)*-1})-90)+{round((get_highest_value(sunrises)+get_lowest_value(sunrises))/2)}'

	print(f'{year} Sunrise Eqautions: {sunrise_sin_equation} | {sunrise_cos_equation}')
	print(f'{year} Sunset Eqautions: {sunset_sin_equation} | {sunset_cos_equation}')


window = sg.Window('controller', load_layout(), resizable=True)

while True:
	for event in pygame.event.get():
		if event == pygame.QUIT:
			exit()
	
	event, values = window.read()
	match event:
		case 'DISPLAY':
			drawGraph(surface, values['_LINE_COLOR_'], pen_width, spacer, screen_resolution, values['_BACKGROUND_COLOR_'])
			for year in years:
				if values[f'_{year}_HIDE_'] == True:
					continue

				if int(values['_DATE_INPUT_']) >= 32 or int(values['_DATE_INPUT_']) <= 0:
					continue

				if int(values['_DATE_INPUT_']) >= 29:
					print('WARNING: data becomes EXTREMELY unreliable at this date, some months do not contain this date and thus will break')
				
				display(surface, screen_resolution, year, values['_LOCATION_'], values[f'_{year}_SUNSET_COLOR_'], values[f'_{year}_SUNRISE_COLOR_'], values['_DATE_INPUT_'])
		case 'SCRAPE':
			try:
				scrape_data(years=[values['_YEAR_INPUT_']], city=values['_CITY_INPUT_'], location=values['_LOCATION_INPUT_'])
				window.close()
				window = sg.Window('debugger', load_layout(), resizable=True)
			except Exception as error:
				print(error)
		case sg.WIN_CLOSED:
			exit()