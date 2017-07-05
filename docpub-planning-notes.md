# To-do list

* TK: make sure Google oauth works with existing accounts that use the auth'ed domains
	* it seemed to work locally, but not on prod

* TK: handle if someone creates a document with no credentials; right now it creates the obj, but then they couldn't update later bc of obj.created condition. so we need to either do: if no obj.link or obj.file, then...
	* prevent save from initially firing 
	* change save_model method to only choose update method 

* TK: prevent both error messages from appearing? in the case of no password after a doc was previously uploaded, it throws both "re-enter" and "credentials failed" errors, which are redundant

* TK: check user password on save in User admin, which would help fix issue above and make things better

* TK: include newsroom name as field for extended user so we can filter in User admin list view
	* would that even work bc it'd be stored in a FK field?

# Questions

* Q: require everyone to have their own DocCloud.org account to use the tool? 

* Q: set a shared account in the admin so indidivual newsrooms can do their own shared accounts vs just using DC bureau's?

* Q: filter admin by newsroom or individual? currently individual

* Q: email me when finished?

* Q: schedule publish?

* Q: delete PDF after uploaded to avoid excess storage costs?

# Punt

* PUNT: drag-and-drop interface for the form? initially it will just be a standard "click and choose"
	* try jQuery File Upload; basic seems best https://blueimp.github.io/jQuery-File-Upload/basic.html
	* also check out this Django implementation https://github.com/sigurdga/django-jquery-file-upload

* PUNT: create bookmarklet that can grab a PDF open in your browser?
	* enable post API and/or just pre-populate Django admin?
	* e.g. [domain]/admin/docs/document/add/?link=URL

* PUNT: use Google Drive or Issuu for first pass?
	* https://developers.google.com/drive/v3/web/quickstart/python
	* https://developers.issuu.com/
	* https://www.scribd.com/developers (no longer accepting new registrations)

* PUNT: ablity to convert word doc to PDF during file upload?

# Completed

* COMPLETED: for admin fields, note which are displayed publicly 

* COMPLETED: doccloud creds in django user; if not, then use master account 
	
* COMPLETED: Only show logged in user the files they have uploaded?
	* Q: worth filtering by the org, when present?

* COMPLETED: workflow
	* add / edit
	* view form
	* submit + get embed code

* COMPLETED: use admin inlines for batch upload

* COMPLETED: click to copy the embed code in the admin:
	* e.g. https://codepen.io/shaikmaqsood/pen/XmydxJ/

* COMPLETED: media queries for iframe embed

* COMPLETED: use Google oauth for login
	* https://python-social-auth.readthedocs.io/en/latest/configuration/django.html

* COMPLETED: encrypt DocumentCloud password

* COMPLETED: PDF file storage
	* S3? https://github.com/bradleyg/django-s3direct