# **FARMFUND**

#### **Video Demo:**  https://youtu.be/Vah13bH4LDE

#### **Description:**
Farmfund web app is a secure social investment platform for agriculture and small medium enterprises established to raise and empower farmers in Nigeria and Africa at large. It is a platform built to work with diasporas to support their local communities in Africa through the offer of investments and consultancy to local farmers to help commercialize farming in Africa.

#### **Details of Each file:**
##### **_1. layout.html_**
The layout.html contains both the navigation menu and the footer page.

The navigation menu is comprised of the logo of the platform, the home/root menu, the dashboard, the projects, the services, the uploads or fund or invest, the contact, the logout and settings menus when a user is logged in but comprised of the platform logo, the login menu and the register menu when no user is logged in.

The footer page is comprised of a get started button that links one to the register page when clicked. It also carries technical support, payment/fund, farmfund, about, login, register and portfolio buttons that opens up the support, fund, index, services, login, register and projects pages. There are also contact buttons to call for supports or send direct messages to the admin.

The footer also houses the social media platforms, the copyright and cs50x link.

##### **_2. register.html_**
The register page is the sign up page that requires the user to provide some of his/her details that will be saved in the backend which the user would require to login.

The register page carries a text input, an email input, two password inputs, three radio inputs and a submit button. The text input requires for a username, the email input requires the user's email address, the two password inputs requests for the user's password and its confirmation, the three radio buttons are for the user tracks (Farmer, Investor or Consultant) which a user can select only one out of the three. Then the submit button submits the user's details to the backend.

##### **_3. login.html_**
The login page logs a user into the platform thereby allowing the user full access into all the parts of the platform.

The login page contains a text input for the username, a password input for the user's password and a submit button that submits the login details which if the details are correct and contained in the database the user is logged in and redirected to the home page

##### **_4. index.html_**
The index.html is the root page of the file that shows the introduction of the platform, the maximum of five most recent projects, a button to show all farms and another to fund a particular farm, the acclaimed partners of the platform.

If a user is not logged in the page will be redirected to the login page instead of the root page.

##### **_5. dashboard.html_**
The user dashboard contains all the dealings of the user depending on whether the user is a farmer, an investor or a consultant.

It contains a sub-menu carrying three menu items of home, transactions and projects.

The home shows all the details partaining to the user including the investments received or offered, conultations received or given, amount needed and raised if user is a farmer, farms served if the user is a consultant, farms invested on, expected profit and return on investment if the user is an investor.

The transactions menu contains a table showing the transaction history of the user while the projects menu shows all the projects the user is involved in.

##### **_6. projects.html_**
The projects page embodies all the projects the being carried out by the users of the platform.

##### **_7. services.html_**
The services page shows all the details about the platform including what the platform does and how it is done.

##### **_8. uploads.html_**
The uploads page allows a farmer user to uplaod the required details of his/her farm.

##### **_9. fund.html_**
The fund page allows an investor user to invest on the available farms in the platform.

##### **_10. consult.html_**
The consult page allows a consultant user to offer his/her consultancy to the available farms in the platform.

##### **_11. contact.html_**
The contact page contains the full contacts of the platform including a map showing the office address and the direction to the office.

##### **_12. farms.db_**
The farms.db is an sqlite3 database containing 3 tables - users, transactions and farms.
The users table contains every users personal from the register page details. The farm table contains every farm information as it is sent from the uploads page. The transactions table contains every deal from the fund and consult pages.

##### **_13. app.py_**
The app.py file contains all python codes controlling the backend of the platform.

##### **_14. helpers.py_**
The helpers.py file contains all python codes defining such python functions as error function, login_required function and NGN function that are used in the app.py.

##### **_15. app.js_**
The app.js file contains all javascript codes used to show the active menu in the dashboard as well as farm pages.

##### **_16. styles.css_**
The styles.css file contains all cascading style sheet codes used to design/decorate the entire pages of the platform.

##### **_17. settings_**
The settings button is comprised of settings.html, updatepassword.html and useraccount.html. Their functions include settings page white opens up the link to the page to change user password and the page to display user account informations.

##### **_18. requirements.txt_**
The requirements.txt file contains all information about all the libraries, modules, and packages in itself that are used while developing this platform.