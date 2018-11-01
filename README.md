===
django-verdict
=====

Verdict is a simple Django app to manage permission. 


Quick start
-----------

##### 1. Add `verdict` to your `INSTALLED_APPS` setting

```
    INSTALLED_APPS = (
        ...
        'verdict',
    )
   
``` 

 * if want use redis cache: 

```
    INSTALLED_APPS = (
        ...
        'cacheops',
        'verdict',
    )
    
    VERDICT_SETTINGS = {
    	...
    	'CACHE': {
    		'host': '127.0.0.1',
    		'port': 6379,
    		'db': 1,
    		'password': 'localpw'
    	}
    }
   
```

##### 2. Include the verdict URLconf in your project`s urls.py
	
```
url(r'^verdict/', include('verdict.urls', namespace='verdict')),
```
    
   * `namespace='verdict'` is required.

##### 3. create the verdict models

```
python manage.py migrate
```

##### 4. Start the development server

```
python manage.py runserver
```

##### 5. Visit website to use verdict

```
http://127.0.0.1:8000/verdict/
```