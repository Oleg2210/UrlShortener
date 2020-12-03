# UrlShortener
UrlShortener is a small Django project. Its functionality provides the following features:
- create and store shortened links
- access your shortened links and edit them
- redirect to a long link by entering a short one

# Running
To run Url Shortener you need to install `docker` and `docker-compose`. You can see how to do this here https://docs.docker.com/. 
After you have done this, go to the root directory of the project, start the console and enter the following command:
```
$ docker-compose up
```
The first launch of a project may take several minutes, but subsequent launches will be much faster. 
The project is available on port 80 at 127.0.0.1
If you see a 502 error from Nginx in the browser, it means that django has not started yet. Wait a few more seconds and reload the page.

# Implementation details
- There is no authorization on the site. The data is stored reference to the `session`. This is implemented with a single Django `model` - ShortenedUrl. It has only three fields: session (foreign key to sessions table), shortened_id (primary key) and link (link to be shortened).
- The session lifetime is determined by the environment variable - SESSION_TTL. By default, it is 604800 seconds, which corresponds to one week. After each visit to the site, the session lifetime is updated
- Every day at 00:00, utc `cron` deletes expired sessions and related shortened links. The cronfile can be found at `/shortener/cronfile`.
- There is also  `Redis cache`. In the moment user requests a link for the first time, it gets into the cache. In a situation when a new link is created, and at the same time it is already present in the cache, the value in the cache is overwritten. This situation is when a link remains in the cache that is no longer in the database. The time of presenting a link in the cache is determined by the environment variable CACHE_TTL = 86400(one day).
- Django Rest framework is used to implement API, it provides API development tools and provides a user-friendly interface.
- After launch, `volumes` directory will appear in the root directory. It will store the information necessary to restart the program (for example, database data). Also here you will find logs of django and `cron`.
- All `environmental variables` are available on `/envs/`. All `Django files` available on `/shortener/app/`


.


