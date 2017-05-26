*FIELDS*

***your info***
* name (only if they don't have an account; scratch this in favor of just email?) 
	* pass along via key/value metadata feature?
* email (whether they do or do not have an account)
	* if they do, then it will publish to their account
	* if not, it will publish to DocCloudAdmin-type account
* password (optional)
	* hide it from view like password fields do
* newsroom (drop-down)
	* pass in key-value pair

***doc info***
* title
* description
* source (don't include if it's leaked/confidential)
* file upload 
	* do we even need to store the PDF or can we just stream it?
	* if it needs to be stored, then probably best to delete after uploaded to avoid huge storage costs
* or link to PDF

***publishing info***
* email me when finished
* ??? related article URL 
* ??? published URL
* access level
* schedule publish
* link to document viewer
* embed code

*EMBED CODE*
* minify it? yes, less likely for incomplete or error in copy-paste
* one-click button to copy and/or click within the field to select-all automatically

*NOTES*
* drag-and-drop interface for the form? initially it will just be a standard "click and choose"
	* try jQuery File Upload; basic seems best https://blueimp.github.io/jQuery-File-Upload/basic.html
	* also check out this Django implementation https://github.com/sigurdga/django-jquery-file-upload
* use Google oauth for login?
* create bookmarklet that can grab a PDF open in your browser?