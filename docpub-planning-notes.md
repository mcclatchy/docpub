# To-do list

* TK: Is there a good solution for populating a user's newsroom field in `DocumentCloudCredentials` when no password is present?
	* we would need a new model (`UserInfo`? `UserMeta`), but would it have any info beyond `newsroom`?

* TK: re-enable adding username to doccloud k-v pair metadata

* TK: ability to include newsroom even if there's no password

* TK: welcome email template with account information

* TK: send emails
	* `new_user` to superadmin after user signs up
	* `confirmation` to user after they get perms
	* `welcome` to new user after superadmin adds them

* TK: if email domain not whitelisted, update oauth process to redirect to a page that says `Thanks for registering! Your account has been sent to an administrator for approval`

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

* COMPLETED: check user password on save in User admin, which would help fix issue above and make things better

* COMPLETED: avoid need for second save on user edit page re: checking password bc it needs to save on FK'ed model first

* COMPLETED: handle if someone creates a document with no credentials; right now it creates the obj, but then they couldn't update later bc of obj.created condition. so we need to either do: if no obj.link or obj.file, then...
	* prevent save from initially firing 
	* change save_model method to only choose update method 
	* SOLUTION: if documentcloud_id, then update; otherwise, upload

* COMPLETED: make sure Google oauth works with existing accounts that use the auth'ed domains
	* it seemed to work locally, but not on prod

* N/A: prevent both "add doc" page error messages from appearing? in the case of no password after a doc was previously uploaded, it throws both "re-enter" and "credentials failed" errors, which are redundant
	* UPDATE: unneeded now bc creds checked in user edit page

* COMPLETED: update `login.html` to emphasis google sign-in

* COMPLETED: include newsroom name as field for extended user so we can filter in User admin list view
	* would that even work bc it'd be stored in a FK field? it should work like `obj.documentcloudcredentials.newsroom`
	* under DocCloudCreds, add newsroom field
	* under UserAdmin add to save method a way to popular based on user email  
	* under UserAdmin add `list_display` field to display the newsroom name

* COMPLETED: how to handle non-Mclatchy whitelisted email domains? (e.g. gmail)
	* Solution: try/except statement

* COMPLETED: how to mark an account as `verified` after the test has occurred? currently only updates that field during the test upload

* COMPLETED: add a custom formatted `list_display` field that displays a checkmark or x depending on whether the user has included a verified DocumentCloud password
	* need to add a `verified` field under DocCloudCreds

* COMPLETED: let users create an account even if not previously set up and automatically set them as staff with necessary perms
	* https://python-social-auth-docs.readthedocs.io/en/latest/pipeline.html#extending-the-pipeline

* COMPLETED: Slack output when new user logs in with oauth

* COMPLETED: update `account` field to pull from choices listing `shared` or `individual`

* COMPLETED: remove `View site`in Django admin

* COMPLETED: fix 403 error when when signing in with Google oauth
	* `accounts/login` not found in URLs, but not an issue when logging with existing user

* COMPLETED: fix `user` if uploaded to shared? Ben C uploaded one with shared account and it showed him as the owner, not shared account as owner

* N/A: Ben C got `documentcloud_login` referenced before assignment, which he shouldn't get bc doc uploaded to the shared acct; must be related to fact that it thinks it was uploaded to individual instead of shared acct

* COMPLETED: if uploaded to shared account, give warning that user won't be able to view if access set to `Your newsroom` and don't have the shared account credentials (maybe don't say the second part tho)

* COMPLETED: add boolean field to doccloud creds to indicate whether encrypted (default is False)

* COMPLETED: make the conditional under `save_model` for `UserAdmin` bulletproof; currently it would not work properly if a user's DocumentCloud password included an = at the end, like the encrypted passwords all do
	* e.g. starts with `gAAA` or ???
	* better solution? add a field indicating password status (empty, unsecure, secure); e.g. empty is when it's `''` or `None`, unsecure 1) is when it was empty and is now not or 2) the last one doesn't match the current one before encrypting

