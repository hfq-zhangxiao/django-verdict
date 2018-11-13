=====
django-verdict
=====

Verdict is a simple Django app to manage permission. 


Quick start
-----------

1. Add "verdict" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'verdict',
    )
    
    * if want use redis cache: 

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

2. Include the verdict URLconf in your project urls.py like this::

    url(r'^verdict/', include('verdict.urls')),

3. Run `python manage.py migrate` to create the verdict models.

4. Start the development server with `python manage.py runserver`.

5. Visit http://127.0.0.1:8000/verdict/ to use verdict.