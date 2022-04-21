


import re

from car_tracker.constants import MAKES



def parseTitle(title):
	data = {}

	makes = re.findall('|'.join(['\\b{}\\b'.format(make['name']) for make in MAKES]), title, re.IGNORECASE)
	if makes:
		data['make'] = makes[0]

		models = re.findall(r"{}([ \d \w \. \- \' \/ \\]+)".format(data['make']), title, re.IGNORECASE)
		if models:
			data['model'] = models[0]

	years = re.findall(r'[1-2][0-9]{3}', title)
	if years:
		data['year'] = years[0]

	return data



def parseMileage(mileage):
	if ('KM' in mileage.upper()) or ('KILOMETERS' in mileage.upper()):
		kilometers = True
	elif ('k' in mileage):
		mileage = mileage.replace('k', '000')
		kilometers = False
	else:
		kilometers = False

	if ('TMU' in mileage.upper()):
		tmu = True
	else:
		tmu = False

	parsed_mileage = re.findall(r"\d+", mileage.replace(',', ''))[0]
	#parsed_mileage = ''.join([x for x in mileage if (x in ['0','1','2','3','4','5','6','7','8','9'])])
	return parsed_mileage, kilometers, tmu




def parsePrice(price):
	parsed_price = ''.join([x for x in price if (x in ['0','1','2','3','4','5','6','7','8','9'])])
	return parsed_price
