# Pellet

Pellet helps your applications performance by warning against `N+1` queries. The Django ORM makes it easy to forget using `select_related` and `prefetch_related` correctly and can accidentally cause `N+1` queries to happen.

Pellet aims to recreate [Bullet](https://github.com/flyerhzm/bullet) for Django. 
