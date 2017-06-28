*FIELDS*


***publishing info***
* email me when finished (TK?)
* schedule publish (TK?)

*EMBED CODE*
* one-click button to copy and/or click within the field to select-all automatically
	* https://codepen.io/shaikmaqsood/pen/XmydxJ/
* how to handle for mobile apps? just construct iframe embed from DocumentCloud html version
	* generate upload html file with embed code to S3 and provide iframe?
	* pre-fix code to control display
		* leave as is on desktop
		* hide script embed and link directly to doc viewer on apps? check for jquery?
	* generic PDF or `thumbnail_image_url` icon to open in-app browser?
		* having issues with this; will we need to grab and host on S3?

*NOTES*
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

* Q: require everyone to have their own DocCloud.org account to use the tool?

* TK: include newsroom name as field for extended user so we can filter in User admin list view

* TK: media queries: 400 or 450 for phone, 600 for desktop (suggestion via Nathaniel)

* IN PROGRESS: use Google oauth for login?
	* https://developers.google.com/api-client-library/python/start/get_started
	* https://developers.google.com/api-client-library/python/guide/django
	* https://artandlogic.com/2014/04/tutorial-adding-facebooktwittergoogle-authentication-to-a-django-application/

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

* UNNECESSARY: file storage
	* S3? https://github.com/bradleyg/django-s3direct
	* do we even need to store the PDF or can we just stream it?

* Q: delete PDF after uploaded to avoid excess storage costs?