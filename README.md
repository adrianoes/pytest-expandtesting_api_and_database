# pytest-expandtesting_api_and_database

Database and API testing in [expandtesting](https://practice.expandtesting.com/notes/api/api-docs/) api docs. This project contains basic examples on how to use Pytest to test database, API and how to combine database and API tests writen in Python. Good practices such as hooks, custom commands and tags, among others, are used. All the necessary support documentation to develop this project is placed here. Although custom commands are used, the assertion code to each test is kept in it so we can work independently in each test. Requests library is used to deal with API tests. It creates one .json file for each test so we can share data between different commands in the test. The .json file is excluded after each test execution. 

# Pre-requirements:

| Requirement                     | Version        | Note                                                            |
| :------------------------------ |:---------------| :-------------------------------------------------------------- |
| Microsoft Visual C++            | 14.42.34438.0  | -                                                               |
| MySQL Community Server          | 8.4.4          | -                                                               |
| MySQL Workbench                 | 8.0.41         | -                                                               |
| DbGate Community edition        | 6.3.2          | -                                                               |
| Python                          | 3.12.5         | -                                                               |
| Visual Studio Code              | 1.89.1         | -                                                               |
| Python extension                | 2024.14.1      | -                                                               | 
| mysql-connector-python          | 9.2.0          | -                                                               |
| Pytest                          | 8.3.3          | -                                                               |
| Faker                           | 30.0.0         | -                                                               |
| requests                        | 2.32.3         | -                                                               |
| pytest-html                     | 4.1.1          | -                                                               |
          
# Installation:

- See [Microsoft Visual C++ Redistributable latest supported downloads page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) and download the latest X64 version. Double click the downloaded file, :white_check_mark:**I agree to the license terms and conditions**, :point_right:**Install**, :point_right:**Yes** to allow changes in your device and :point_right:**Restart**.  
- See [MySQL Community Downloads page](https://dev.mysql.com/downloads/mysql/) and on Select Version dropdown list, select the LTS versions that is being displayed. For the Windows (x86, 64-bit), MSI Installer, :point_right:**Download**, :point_right:**No thanks, just start my download.**. Click on the downloaded file, :point_right:**Next**, :white_check_mark:**I accept the terms in the License Agreement**, :point_right:**Next**, :point_right:**Typical**, :point_right:**Install**, :point_right:**Yes**, :white_check_mark:**Run MySQL Configurator**, :point_right:**Finish**, :point_right:**Yes**, :point_right:**Next**. Wait for the MySQL Configurator to open and :point_right:**Next**, :point_right:**Next**, :point_right:**Next** (keep default network config e.g. Port: 3306), input a password in the required fields, :point_right:**Next**, :point_right:**Next**, :point_right:**Next**, :point_right:**Next**, :point_right:**Execute** and :point_right:**Next**, :point_right:**Finish**.
- Right click :point_right: **My Computer** and select :point_right: **Properties**. On the :point_right: **Advanced** tab, select :point_right: **Environment Variables**, and then edit Path system variable with the new C:\Program Files\MySQL\MySQL Server 8.4\bin entry. Open Powershell terminal and execute ```mysql -u root -p``` along with previous defined password when asked. This actions will allow the use of MySQL in the command line.
- See [MySQL Workbench page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) and, for the Windows (x86, 64-bit), MSI Installer, :point_right:**Download**, :point_right:**No thanks, just start my download.**. Click on the downloaded file, :point_right:**Next**, :point_right:**Next**, :point_right:**Next**, :point_right:**Install**, :point_right:**Yes** and :point_right:**Finish**. Wait for MySQL Workbench to open and, in the MySQL Connections frame, click on Local Instance MYSQL84, input your previous defined password and :white_check_mark:**Save password in vault** (so no retyping password will be required), :point_right:**OK**, :white_check_mark:**Don't show this message again**, :point_right:**Continue Anyway**. 
- See [DbGate Community edition page](https://dbgate.org/download/) and, for windows, :point_right:**Installer**. Clcik on the downloaded file and wait for the installation to be finished and DbGate to be open. On Connection type dropdown list, :point_right:**MySQL**, input root and your previous defined password in user and passwword fields respectively, :point_right:**Save** and :point_right:**Connect**.
- See [python page](https://www.python.org/downloads/) and download the latest Python stable version. Start the installation and check the checkboxes below: 
  - :white_check_mark: Use admin privileges when installing py.exe 
  - :white_check_mark: Add python.exe to PATH
and keep all the other preferenced options as they are.
- See [Visual Studio Code page](https://code.visualstudio.com/) and install the latest VSC stable version. Keep all the prefereced options as they are until you reach the possibility to check the checkboxes below: 
  - :white_check_mark: Add "Open with code" action to Windows Explorer file context menu. 
  - :white_check_mark: Add "Open with code" action to Windows Explorer directory context menu.
Check then both to add both options in context menu.
- Look for Python in the extensions marketplace and install the one from Microsoft.
- Open windows prompt as admin and execute ```pip install mysql-connector-python``` to install mysql-connector-python plugin.
- Open windows prompt as admin and execute ```pip install pytest``` to install Pytest.
- Open windows prompt as admin and execute ```pip install Faker``` to install Faker library.
- Open windows prompt as admin and execute ```pip install requests``` to install Requests library.
- Open windows prompt as admin and execute ```pip install pytest-html``` to install pytest-html plugin.
- Open windows prompt as admin and execute ```pip install python-dotenv``` to install python-dotenv.

# Tests:

- Execute ```pytest ./tests -v --html=./reports/report.html``` to run tests in verbose mode and generate a report inside reports folder.
- Execute ```pytest ./tests/api/users_api_test.py -k create_user_api -v --html=./reports/report.html``` to run tests that contains "create_user_api" in its structure inside users_api_test.py file in verbose mode and generate a report inside reports folder.

# Support:

- [expandtesting API documentation page](https://practice.expandtesting.com/notes/api/api-docs/)
- [expandtesting API demonstration page](https://www.youtube.com/watch?v=bQYvS6EEBZc)
- [Installing MySQL on Windows - 2025 Full Tutorial (MySQL, MySQL Workbench, DbGate)](https://www.youtube.com/watch?v=50CQoMs4vRo)
- [MySQL Installation on Windows - Zarko’s Video Tutorial](https://zarkomaslaric.notion.site/MySQL-Installation-on-Windows-Zarko-s-Video-Tutorial-1b8fe1ebfde28066a86ac6b7eb401cb7)
- [Try-SQL Editor](https://www.w3schools.com/sql/trysql.asp?filename=trysql_op_or)
- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)
- [Pytest](https://docs.pytest.org/en/stable/)
- [Using faker with selenium and python](https://stackoverflow.com/a/27650137/10519428)
- [Faker 30.0.0 documentation](https://faker.readthedocs.io/en/stable/)
- [Python For Loops](https://www.w3schools.com/python/python_for_loops.asp)
- [Python – Call function from another file](https://www.geeksforgeeks.org/python-call-function-from-another-file/)
- [Setting Up and Tearing Down](https://www.selenium.dev/documentation/webdriver/getting_started/using_selenium/#setting-up-and-tearing-down)
- [Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it #1653](https://github.com/urllib3/urllib3/issues/1653#issuecomment-512794112)
- [Requests: HTTP for Humans™](https://requests.readthedocs.io/en/latest/)
- [How to get the localStorage with Python and Selenium WebDriver](https://stackoverflow.com/a/46361890/10519428)
- [Python Requests Library Complete Tutorial - Rest API Testing](https://www.youtube.com/watch?v=LP8NlUYHQGg)
- [Python Accessing Nested JSON Data [duplicate]](https://stackoverflow.com/a/23306717/10519428)
- [Write JSON data to a file in Python](https://sentry.io/answers/write-json-data-to-a-file-in-python/)
- [Read JSON file using Python](https://www.geeksforgeeks.org/read-json-file-using-python/)
- [Python | os.remove() method](https://www.geeksforgeeks.org/python-os-remove-method/)
- [ImportError: No module named 'support'](https://stackoverflow.com/a/56268774/10519428)
- [Python String strip() Method](https://www.w3schools.com/python/ref_string_strip.asp)
- [distutils](https://docs.python.org/3/library/distutils.html)
- [ChatGPT](https://openai.com/chatgpt/)

# Tips:

- API tests to verify a password reset token and reset a user's password must be tested manually as they rely on e-mail verification. 
- delete_note_api was created only with the practice purpose since there is the possibility to delete the user right away. 
- Trust ChatGPT.
- This project was developed in VSC. Problems regarding non accessed arguments were faced. Argumetns were presented in translucid form (not accessed) but were required for the correct execution of the test. Attempt to use Pycharm Is recommended. 
