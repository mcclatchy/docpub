*FIELDS*

***your info/usermodel***
* name (only if they don't have an account; scratch this in favor of just email?) 
	* pass along via key/value metadata feature?
* email (whether they do or do not have an account)
	* if they do, then it will publish to their account
	* if not, it will publish to DocCloudAdmin-type account
* password (optional)
	* hide it from view like password fields do
* newsroom (drop-down)
	* pass in key-value pair

***publishing info***
* email me when finished
* ??? related article URL 
* ??? published URL
* schedule publish

*EMBED CODE*
* one-click button to copy and/or click within the field to select-all automatically
	* https://codepen.io/shaikmaqsood/pen/XmydxJ/
* how to handle for mobile apps?
	* generate upload html file with embed code to S3 and provide iframe?
	* pre-fix code to control display
		* leave as is on desktop
		* hide script embed and link directly to doc viewer on apps? check for jquery?
	* generic PDF or `thumbnail_image_url` icon to open in-app browser?
		* having issues with this; will we need to grab and host on S3?

*NOTES*
* why does documentcloud_object not work inside the Document class for upload and not outside for updating? right now it's duplicated, grrr...
* COMPLETE: for admin fields, note which are displayed publicly 
* PUNT: doccloud creds in django user; if not, then use master account 
	* this is tough bc then file edits by another user don't work and you end up recreating the DocumentCloud.org admin
* UNNECESSARY: file storage
	* S3? https://github.com/bradleyg/django-s3direct
	* do we even need to store the PDF or can we just stream it?
	* if it needs to be stored, then probably best to delete after uploaded to avoid huge storage costs
* COMPLETE: workflow
	* add / edit
	* view form
	* submit + get embed code
* TK: drag-and-drop interface for the form? initially it will just be a standard "click and choose"
	* try jQuery File Upload; basic seems best https://blueimp.github.io/jQuery-File-Upload/basic.html
	* also check out this Django implementation https://github.com/sigurdga/django-jquery-file-upload
* TK: use Google oauth for login?
	* https://developers.google.com/api-client-library/python/start/get_started
	* https://developers.google.com/api-client-library/python/guide/django
	* https://artandlogic.com/2014/04/tutorial-adding-facebooktwittergoogle-authentication-to-a-django-application/
* TK: use Google Drive or Issuu for first pass?
	* https://developers.google.com/drive/v3/web/quickstart/python
	* https://developers.issuu.com/
	* https://www.scribd.com/developers (no longer accepting new registrations)
* TK: create bookmarklet that can grab a PDF open in your browser?
* TK: ablity to convert word doc to PDF during file upload?
* TK: should each newsroom get a "project"?
* NOTE: basically I should require everyone to have their own account to use the new
* TK: media queries: 400 or 450 for phone, 600 for desktop (suggestion via Nathaniel)