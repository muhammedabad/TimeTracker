# Welcome To The Tangent Time Tracker #

### Overview ###

This app provides a single interface to capture your timesheets and sync them to other platforms.

### Supported Integrations ###

- [RiseApp](https://my.riseapp.co.za)
- [Jira](https://www.atlassian.com/software/jira)


### Requirements ###
- RiseApp: Your personal API key and User ID
- Jira: Your instance URL (e.g. test.atlassian.net) and your API key.


### Usage ###
- Once you've obtained your login credentials, go to the "Users" section and edit your profile to include your Integration Settings

![image](https://github.com/user-attachments/assets/e50b0010-ddcc-4d30-858e-6717d72e5f52)


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
- Once you have cloned the project, create an `env.dev` file (template [here](https://github.com/muhammedabad/TimeTracker/blob/main/env.dev.sample) and simply run `make dup` to get started.
- Other common operations related to Django & Docker can be found in the [Makefile](https://github.com/muhammedabad/TimeTracker/blob/main/Makefile)
- For development purposes, you can safely override any settings by creating a `local_settings.py` in the `time_tracker` folder. This file will be ignored by the `gitignore` config.




