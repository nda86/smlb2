### Задача: организация обмена данными между двумя торговыми программами (S-Market, Litebox)
##### Используемые технологии: 
 * Python 3 
 * Django/DRF 
 * Postgres 
 * Docker

##### Реализация: проект состоит из 3 взаимосвязанных микросервисов, и представляет из себя REST API сервер на Django Rest Framework.


## Примечание
Проект был написан мной в декабре 2018 года. Заказчик имел 4 торговых точки с кассами Litebox и единую товароучетную систему S-Market. Была задача организовать обмен данными между этими программами. Весь код был написан в сжатые сроки и сразу был развернут на vps.
С момента начала работы код никак не рефакторился и не модифицировался, не улучшался. Были только правки в соответствии с изменяющимся API Litebox.

В настоящее время заказчик продукта сменил товароучетную программу S-Market, поэтому данный проект больше не используется.


## License
SMLB2 is distributed under the GNU General Public License v3.0 (GPLv3).
