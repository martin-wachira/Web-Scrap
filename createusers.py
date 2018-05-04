import time, getpass,sys,os
from selenium import webdriver
import pandas as pd

#browser = webdriver.PhantomJS()
#browser = webdriver.Chrome()
browser = webdriver.Firefox()
#URLs
LOGIN_URL = "http://localhost:8080/afyaehms/login.htm"
HOME_URL = "http://localhost:8080/afyaehms/referenceapplication/home.page"
CREATE_USER = "http://localhost:8080/afyaehms/admin/users/user.form?createNewPerson=true"
def login():
	url = LOGIN_URL
	browser.get(url)
	time.sleep(2)
	username = browser.find_element_by_id('username')
	username.send_keys('admin')
	time.sleep(1)
	password = browser.find_element_by_id('password')
	print('Please enter the password of admin')
	pass_ = getpass.getpass()
	password.send_keys(pass_)
	submit = browser.find_element_by_name('Submit')	
	submit.click()
	time.sleep(3)
	if browser.current_url == HOME_URL:
		print('Succesfully logged in ')
	else:
		print("Login Failed")
		browser.quit()
		retry = str(input('Do you want to try again?y/n:'))
		if retry.lower() == 'y':
			main()
		else:
			print('Exiting, bye')
			browser.quit()
			sys.exit()
	
	browser.get(CREATE_USER)




def get_data(source_file):
	try:
		data = pd.read_csv(source_file)
	except Exception as e:
		print(str(e))
		browser.quit()
		sys.exit()
	
	
	#Check if username field is duplicated
	duplicates = data[data.username.duplicated(keep=False)]
	duplicates.to_csv('duplicated.csv', index=False)
	
	#remove the user with the same usernames
	if len(duplicates) > 0 :
		print('There were some duplicated users that were not\n'
		'created and were saved on', os.path.abspath('duplicated.csv'))
		data = data.drop(duplicates.index)
	
	#remove the duplicated users
	data = data.drop_duplicates()
	
	return data

def fill_form():
	data = get_data(sys.argv[1])
	created_users = []
	for i in range(len(data)):
		print('[+] Creating user', data.iloc[i]['username'],'[+]')
		try:
			given_name = browser.find_element_by_name('person.names[0].givenName')
			last_name = browser.find_element_by_name('person.names[0].familyName')
			password = browser.find_element_by_name('userFormPassword')
			password_again = browser.find_element_by_name('confirm')
			username = browser.find_element_by_name('username')
			browser.find_element_by_id(data.iloc[i]['sex']).click()
		except Exception as e:
			print('Sorry,:',str(e))
			browser.quit()
			sys.exit()
		given_name.send_keys(data.iloc[i]['firstname'])
		last_name.send_keys(data.iloc[i]['lastname'])
		username.send_keys(data.iloc[i]['username'])
		password.send_keys(data.iloc[i]['password'])
		password_again.send_keys(data.iloc[i]['password'])
		
		usertype = data.iloc[i]['usertype']
		
		if usertype == 'pharmacy':
			print('The user is a pharcasist')
			print('Giving roleStrings.Pharmacy')
			browser.find_element_by_id('roleStrings.Pharmacy').click()
			
		elif usertype == 'doctor':
			print('The user is a doctor')
			print('Giving roleStrings.Doctor')
			browser.find_element_by_id('roleStrings.Doctor').click()
			browser.find_element_by_id('roleStrings.MCHClinicUser').click()
			browser.find_element_by_id('roleStrings.MCHTriageuser').click()
			browser.find_element_by_id('roleStrings.RegistrationClerk').click()
			
		elif usertype == 'mch':
			print('The user is a MCH user')
			print('Giving roleStrings.MCHClinicUser')
			browser.find_element_by_id('roleStrings.MCHClinicUser').click()
			browser.find_element_by_id('roleStrings.MCHTriageuser').click()
			browser.find_element_by_id('roleStrings.RegistrationClerk').click()
			
		elif usertype == 'regclerk':
			print('The user is a regclerk')
			print('Giving roleStrings.RegistrationClerk')
			browser.find_element_by_id('roleStrings.RegistrationClerk').click()
			
			
		browser.find_element_by_id('saveButton').click()
		time.sleep(2)
		errors = []
		elem_one = browser.find_elements_by_xpath('.//span[@class = "error"]')
		elem_two = browser.find_elements_by_xpath("/html/body/div[1]/div[3]/form/fieldset[1]/table/tbody/tr[4]/td[2]/span")
		elem_three = browser.find_elements_by_xpath("/html/body/div[1]/div[3]/div[3]")
		if elem_one:
			for el in elem_one:
				if el.text != None:
					errors.append(el.text)
		if elem_two:
			for el in elem_two:
				if el.text != None:
					errors.append(el.text)
		if elem_three:
			for el in elem_three:
				if el.text != None:
					errors.append(el.text)
					
		if len(errors)>0:
			for e in errors:
				print("ERROR::The user could not be created because:", e)
				print()
		else:
			created_users.append(data.iloc[i])
			print('Succesfully created the user:',data.iloc[i]['username'])
			print()
		
		time.sleep(1)
		browser.get(CREATE_USER)
	if len(created_users) > 0:
		users = pd.concat([x for x in created_users], axis=1)
		df = pd.DataFrame(users)
		df = df.T
		df = df.drop('password', 1)
		df.T.to_csv('created')
		print('\n CREATED USERS')
		print(df.T)
	print('Done,bye!')
		

def main():
	login()
	fill_form()

if __name__== '__main__':
	main()
	browser.quit()