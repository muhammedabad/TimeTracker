# Welcome To The Tangent Time Tracker #

### Overview ###

This app provides a single interface to capture your timesheets and sync them to other platforms.

### Supported Integrations ###

- [RiseApp](https://my.riseapp.co.za)
- [Jira](https://www.atlassian.com/software/jira)


### Requirements ###
- RiseApp: Your personal API key and User ID. To obtain these, log in to Rise and click on the code block next to your name on the right hand side:
  
    ![image](https://github.com/user-attachments/assets/0839a0b0-c508-4cf1-aa8f-51ce3bca5d31)

 

  A pop-up window will appear and display your user ID and API key - in the example below `123` is the user ID and `mysecretoken` is the API key:

   ![image](https://github.com/user-attachments/assets/fe052699-a35d-4a03-8b45-c74fa090b8e0)


- Jira: Your instance URL (e.g. test.atlassian.net) and your API key. You can generate an API key [here](https://id.atlassian.com/manage-profile/security/api-tokens).


### Usage ###
- If you are running this locally, just run `make createsuperuser` to create your user account and follow the prompts.
- Once you've obtained your login credentials, go to the "Users" section and edit your profile to include your Integration Settings.

![image](https://github.com/user-attachments/assets/acfa28f6-4074-44ed-9a0b-ba4a318e6c5f)


- Next, navigate to the **Entries** app and click the **+** icon in the top-right corner and fill in the form below:


- The timesheet date defaults to the current date and can be changed via the datepicker. Note that you may only capture **one** entry per day. All entries have a "Last Synced At" value which indicates when the entry was last updated on the relevant system.

![image](https://github.com/user-attachments/assets/b31291a0-de52-4ae8-b6c0-82961d3711e3)

  
- For Jira entries, fill in:
  -  The Jira ticket number
  -  Minutes spent
  -  Description
    
- For Rise entries, fill in:
  -  Your timesheet info in the **Value** textarea
  -  Hours Worked (defaulted to 8)
  -  Select your Rise Project

### Known Issues / Limitations ###
- Only one Rise entry can be captured per day
- By default, Jira users cannot delete worklog entries. Should you need to remove this you may set the hours worked to 0 on the relevant entry. Rise entries can be deleted.


### Contributing ###

- Feature Requests & Bug Fixes are always welcome! To get started, all you require is [Docker](https://docker.com)
- Once you have cloned the project, create an `env.dev` file (template [here](https://github.com/muhammedabad/TimeTracker/blob/main/env.dev.sample)) and simply run `make dup` to get started.
- Other common operations related to Django & Docker can be found in the [Makefile](https://github.com/muhammedabad/TimeTracker/blob/main/Makefile)
- For development purposes, you can safely override any settings by creating a `local_settings.py` in the `time_tracker` folder. This file will be ignored by the `gitignore` config.




