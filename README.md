# Résumé par semaine

## Semaine 1

J'ai récupéré le matériel que j'utilisais déjà au cours de mon PFE, je n'ai donc pas eu besoin de beaucoup de temps d'installation et de configuration.
J'ai repris le projet là où je l'avais laissé, j'étais en train de chercher à trouver un moyen d'interagir avec le BatteryManager pour obtenir une mesure précise de la batterie restante sur l'appareil (J'obtenais une mesure en pourcentage de batterie restante seulement). J'ai fini par comprendre que la documention officielle Android était erronée, les valeurs censées être retourner par certains appels ne correspondaient pas. J'ai donc expérimenté avec toute les méthodes et appels disponibles et j'ai fini par trouver le bon appel. L'appel à *BATTERY_PROPERTY_CHARGE_COUNTER* était censé fournir la capacité totale de la batterie en microampère-heure mais fourni à la place le résultat de l'appel *BATTERY_PROPERTY_ENERGY_COUNTER*. Cet appel qui renvoie une erreur quand on le teste, est censé renvoyer la batterie restante en microampère.

![Not working](https://github.com/Zetos11/StageM2/blob/main/Figures/Screenshot_20240408-132435.webp?raw=true)

La suite des opérations est logique, maintenant qu'on a une mesure relativement précise de la batterie et qu'on peut faire des suppositions quand à la consommation d'une application sur un certain laps de temps, on continue de chercher à obtenir une meilleure granularitée, si possible en pouvant récupérer le consommation des composants du téléphone (Caméra, GPS, CPU, Ecran, etc.).

## Semaine 2 

L'objectif est donc de récupérer les informations relatives aux rails d'alimentions, qui permettent en théorie d'obtenir la consommation des composants du téléphone.
Les options proposée par le BatteryManager ont était épuisées, il faut donc trouver un autre angle.
Dans le code source d'Android 14, on trouve plusieurs interfaces et classes censées fournir des informations supplémentaires sur la santé de l'appareil et sa batterie.
Malheureusement la plupart d'entre elles sont marqués de l'annotation @hide qui depuis Android 11 empĉhe les développeurs d'interagir avec certaines APIs et interfaces.
Ces mesures sont décrites dans la documentation comme permettants aux dévellopeurs de n'utiliser que des APIs maintenues entre les différentes versions d'Android et d'éviter des applications dépendentes de méthode "cachée". Des développeurs ont trouvé des stratégies pour continuer d'interagir avec ces classes, en utilisant le principe de la réflexion en Java. Il était assez incertain si cette méthode pouvait fonctionner car elle semblait avoir été bloqué par Android depuis 1 an, cependant des posts sur certains forums assuraient que celle-ci était toujurs d'actualité. J'ai donc passé un certain temps à expérimenter avec de la réflexion simple puis de la double réflexion, le meilleur résultat que j'ai pu obtenir était la création d'une instance de l'API caché BatteryConsumer, mais je n'ai jamais réussi à utiliser ses méthodes qui semblait toujours inaccessible.
J'ai trouvé dans l'api SystemHealthDataStats la possibilité de récupérer des mesures liés à la "santé" de l'appareil.
Il semblait donc être possible de récupérer ces donnnées et potentiellement de les croiser avec les valeurs du power_profile.xml 


- Using a .so in CC to access the PowerStatsHAL interface using the native Binder

## Semaine 3

J'utilise le Google Pixel 7 Pro pour mes tests, en étudiant le code de perfetto, il s'avère que l'accès aux rails se fait bien via l'interface **android.hardware.power.stats**. 
Je cherche donc à trouver cette interface directement sur l'appareil pour savoir comment l'utiliser. 
J'ai trouvé un fichier android.hardware.power.stats-service.pixel.rc qui contient des informations à ce sujet (Sur ce chemin : Google Pixel 7 Pro/_/vendor/etc/init/android.hardware.power.stats-service.pixel.rc).
Malheureusement, il s'avère que ces interfaces ne sont pas conçues pour être accessibles de puis la partition "utilisateur" du téléphone. 
Pour les utiliser il faudrait en théorie avoir accès à la partition système. Ce qui pourrait être envisageable en utilisant le VNDK (Vendor Native Developpment Kit) mais je préférerais trouver une autre solution pour répondre à notre problématique.
Je me suis donc finalement retourné vers Perfetto, la solution officielle de Google/Android pour le monitoring de ressource (Smartphone, Web ou Linux).
Je savais que via cette solution je pouvais récupérer mes données liées aux rails d'alimentation mais je voulais l'éviter pour plusieurs raisons :
- Elle ne me permet pas d'implémenter la solution sous la forme d'une application directement sur le téléphone et passera forcément par une application installée sur une machine à côté.
- Je tenais à réussir à repoduire moi mếme cette récupération de donnée, malheureusement même en étudiant le code source je n'ai jamais réussi.
- Les résultats de l'analyse me semblait être dans un format spécifique dédié à un intérpréteur préçis.

J'ai commencé par faire des tests avec un script Shell pour tenter de faire des mesures via Perfetto et ADB, afin d'étudier ce que je récupérais. 
La sortie était encodé en "protobuf binary" pour être utilisé par Perfetto UI, mais un outil de conversion existe pour obtenir les données sous forme d'un Json ou d'un txt.

J'ai donc créé une application en Python, pour l'instant tout en ligne de commande, qui teste la présence d'un téléphone connecté, de la disponibilité des rails d'alimentation sur le modèle testé, puis récupère toute les 250ms les consommations de l'ensemble des rails pendant 60 secondes. 
La deuxième partie consistait à créer un parser pour le fichier de sortie pour récupérer les valeurs utiles du monitoring.

## Semaine 4

J'ai avancé sur l'application en Python, j'ai maintenant un parser fonctionnel pour récupérer mes données de consommations d'énérgies.
Après comparaison entre mon parsing et les résultats obtenues avec la même analyse sur l'outil de visualisation officiel de Perfetto, mes résultats sont concluant et J'obtiens bien la consommation précise du materiel du téléphone.

![Not working](https://github.com/Zetos11/StageM2/blob/main/Figures/powerRails.png?raw=true)

La suite du projet est d'obtenir une meilleure précision, en effet actuellement les mesures représente la totalité de la consommation du téléphone, or nous voulons une précision à l'échelle de l'application pour commencer. 

Avant d'avancer sur la précision j'ai pris le temps de retravailler l'application :

- Ajout d'un listing et de la gestion du package à tester directement depuis l'invite de commande. 
- Ajout d'une méthode de filtre des packages à tester 
- Ajout d'une interface de sélection
- Refactor global du projet pour séparer les fichiers de sorties de l'analyse.
- Gestion d'erreur/d'exception et un peu de documentation

Pour l'instant j'ai laissé tomber l'idée de faire une interface graphique propre au profit d'une app toute en ligne de commande, par soucis de temps et de priorité.

## Semaine 5

La première étape était de réfléchir à la répartition de la consommation de l'application au niveau du matériel.
Par exemple, on peut considérer qu'une application au premier plan du téléphone avec une interface graphique sera responsable de quasiment 100% de la consommation de l'écran. 
En revanche, pour le CPU ou la RAM le calcul est beaucoup plus compliqué.

Pour le CPU, Perfetto propose de nombreuses métriques qui, croisées avec les données du power_profile.xml, permettent d'isoler facilement la consommation d'une application. On peut trouver le détail des exécutions des threads du package testé, plus exactement, on peut savoir quand et sur quel coeur de processeur chaque threads fait ses exécutions. En croisant les intervalles de temps avec les fréquences de chaque coeur pendant les exécutions ainsi qu'avec la consommation de chaque coeur pour une fréquence donnée, on peut trouver la consommation de tout les threads lié à notre application.

Pour la mémoire c'est plus complexe, la solution la plus simple serait de trouver la coût des actions liés à la mémoire.
Malheureusement Perfetto ne permet pas un profiling facile de la mémoire. Pour cela il faudrait que le package testé soit **versionable** ou **debugable** qui sont deux flags Android utilisé pour les tests de performances par les développeurs qui ne sont pas censé rester en production. Les seuls données auxquels nous avont accès pour l'instant sont des quantités de mémoire virtuelle aloué ou le niveau de verouillage de la mémoire de l'application. Ces valeurs ne nous permettent pas de déduire une consommation.

## Semaine 6

Le projet a peu avancé cette semaine avec deux jours fériés et un jour de congé imposé, j'ai profiter des deux jours pour continuer de refactor encore un peu mon code et essayer de le rendre plus efficace, notamment dans la partie parsing.

En effet, afin d'obtenir une meilleure granularitée, je cherchais a obtenir le plus d'informations possible de l'analyse perfetto mais ces traitements supplémentaires commençait non seulement à ajouter du volume inutile à mon code mais également à allourdir la charge côté télépone et ajouter du bruit dans la consommation.

## Semaine 7

Je me suis rapidement rendu compte d'un problème à mesure que je multipliais les métriques que je récupérais via Perfetto, le fichier de sorti devenait (très) volumineux. Il atteignait les huit millions de lignes assez souvent et dépassait les 65mo. Le fichier de sortie de base de l'analyse encodé était plus léger mais l'exploiter dans ma configuration sans le convertir n'était pas envisageable. J'ai essayé de le faire en étudiant le code source de Perfetto mais sans succès, comprendre la structure utilisé dans l'outil était envisageable mais beaucoup trop chronophage et clairement hors sujet. Dans ma configuration actuelle, je parcourais deux fois le fichier complet, une première fois pour récupérer toutes les variables créés au cours de l'analyse qui seront nécessaire au parsing, puis une deuxième fois pour le parsing lui-même. J'ai d'abord retravaillé mon code pour réduire les parcours des données, en stockant toute les données potentiellement intéressante lors du premier parcours pour évacuer toute les lignes inutiles mais cela ne représentait un gain que de 20-25% qui, sans être négligeable, n'était pas sufffisant.

 J'ai fais le choix de réessayer d'utiliser certains outils fournis par Perfetto pour l'analyse. Notamment leur librairie Python qui étant capable de parser le fichier d'analyse encodé pouvait me faire gagner du temps malgré une documentation quasiment inexistante.

## Semaine 8

Ma journée entière du jeudi était dédié à un atelier portant sur le droit neuro-éthique auquel j'ai assisté toute la journée en visio. Ce n'est pas mon domaine du tout et les partis portant spécifiquement sur des aspects précis du droit numérique et commercial était très abstraite mais j'ai pu apprendre beaucoup de chose sur les partis plus en liens avec les pratiques et stratégies des GAFAM (commerce/tracking)

En utilisant la libraire python j'ai réussi à obtenir la consommation (normalement) précise de chaque coeur du processeur pour tout les threads de mon application. Cette mesure ajoutée à la consommation de l'écran pour une application au premier plan représenterait une majorité de la consommation d'énérgie imputable à l'app. Je me suis donc penché sur deux questions importante pour la suite de mon projet :

- Comment faire pour m'assurer que les mesures que j'obtenais était suffisament précise pour en tirer des conclusions ? A quel reférentiel puis-je comparer mes données pour m'en assurer ?
- Dans la suite du projet, l'objectif serait également d'analyser la consommation des TPLs (Third Party Librairies) qu'on retrouve un peu partout dans les applications du stores pour du crash reporting, du monitoring, des publicités... C'est librairies produisent-elles des signatures analysables par le biais de ma solution actuelle ? Le format apk des applications sorties sur le store permet-il le même niveau de précision des mesures que celui que j'obtiens dans le cadre de mes expérimentations ? 

Répondre à cette deuxième question pourrait me donner des éléments de solutions pour la première car si je peux analyser des TPLs sur lesquels Rémy a déjà travailler avec une sonde physique je pourrais au moins avoir une approche de l'ordres de grandeur des variations que je suis censé trouver entre TPLs du même type. Ce qui me permettrait d'estimer la précision de mon analyse en comparant mes résultats aux siens.

Rémy m'a donc fourni les APKs contenant les TPLs sur lesquels il a travaillé, je vais m'en servir dans les semaines qui viennent pour améliorer et tester ma méthode d'analyse.

## Semaine 9

J'ai commencé à travailler avec le APKs, j'ai d'abord testé la présence de threads spécifiques à chacune des TPLs.
J'ai effectivement trouvé des threads créés pour chaque TPLs, ces threads varient comme je m'y attendais, malheureusement aucune convention/règle ne nommage spécifique ne me permet de les identifier à coup sûr.
La meilleure stratégie pourrait consister à analyser d'abord l'APK template qui ne contient aucune TPL, puis comparer les threads de l'APK template avec ceux de l'APK contenant le TPL.

On pourrait ensuite isoler la consommation de ces threads pour obtenir une estimation précise.

En modifiant mon code pour tester les TPLs, je me suis rendu compte que j'avais beaucoup modifié le code du sensor et que les multiples refactor avait beaucoup éloigné l'application de son fonctionnement initial. Je perdais beaucoup de temps pour chaque test à modifier des portions importantes du code.

J'ai donc décidé de créer la 3ème version en retravaillant la forme global du main. J'y ai ajouté plusieurs choses :

- La gestion de plusieurs modes d'exécutions, avec des stratégies différentes pour uniquement la lecture des rails, les tests d'applications au premier plan, les tests de TPLs, avec une implémentation ouverte à l'ajout de nouvelle stratégie.

- J'ai modifié l'entrée en ligne de commande, pour rendre la recherche optionnelle.

- J'ai commencé à travailler sur l'ajout de threading pour pouvoir gérer le scan sur l'appareil et des actions en parallèle.

# Liens Utiles 

## Documentation Android

- https://developer.android.com/reference/android/os/PowerManager
- https://developer.android.com/develop/background-work/services/aidl
- https://developer.android.com/reference/android/os/BatteryManager 
- https://source.android.com/docs/core/power/component
- https://developer.android.com/studio/profile/power-profiler?hl=fr#power-rails
- https://developer.android.com/reference/androidx/benchmark/macro/PowerMetric

## Code Source Android

- https://cs.android.com/android/platform/superproject/main
- https://cs.android.com/android/platform/superproject/main/+/main:external/perfetto/src/android_internal/power_stats.cc
- https://cs.android.com/android/platform/superproject/+/master:hardware/interfaces/power/stats/1.0/IPowerStats.hal
- https://cs.android.com/android/platform/superproject/main/+/main:frameworks/base/core/java/android/os/BatteryConsumer.java;drc=3d19fbcc09b1b44928639b06cd0b88f735cd988d;bpv=0;bpt=1;l=566

## Perfetto

- https://perfetto.dev/
- https://perfetto.dev/docs/
- https://perfetto.dev/docs/reference/trace-config-proto
- https://perfetto.dev/docs/concepts/config
- https://ui.perfetto.dev/

## SO or Reddit useful posts

- https://www.reddit.com/r/AndroidQuestions/comments/xgu8bd/what_is_dalvik/
- https://stackoverflow.com/questions/55970137/bypass-androids-hidden-api-restrictions
- https://stackoverflow.com/questions/31908205/what-exactly-does-androids-hide-annotation-do?noredirect=1&lq=1
- https://stackoverflow.com/questions/15417254/class-forname-throws-classnotfoundexception
- https://www.reddit.com/r/tasker/comments/i94rjj/using_the_java_function_action_to_get_raw_battery/
- https://stackoverflow.com/questions/35449082/how-to-get-the-battery-usage-details-of-installed-apps

## Sidenotes

- Sensor lié au power rails uniquement présent sur les Pixel 6 et plus.
- Power_profile.xml toujours pas accessible facilement sur tout les appareils.
- Pas de heap dump sur une app pas debugable/versionable
- Matplotlib + Seaborn pour les graphs