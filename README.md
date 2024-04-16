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

Next :

- SystemHealthDataStats
- Using a .so in CC to access the PowerStatsHAL interface using the native Binder


# Liens Utiles 

## Documentation Android

- https://developer.android.com/reference/android/os/PowerManager
- https://developer.android.com/develop/background-work/services/aidl
- https://developer.android.com/reference/android/os/BatteryManager
- https://source.android.com/docs/core/power/component
- https://developer.android.com/studio/profile/power-profiler?hl=fr#power-rails

## Code Source Android

- https://cs.android.com/android/platform/superproject/main
- https://cs.android.com/android/platform/superproject/main/+/main:external/perfetto/src/android_internal/power_stats.cc
- https://cs.android.com/android/platform/superproject/+/master:hardware/interfaces/power/stats/1.0/IPowerStats.hal
- https://cs.android.com/android/platform/superproject/main/+/main:frameworks/base/core/java/android/os/BatteryConsumer.java;drc=3d19fbcc09b1b44928639b06cd0b88f735cd988d;bpv=0;bpt=1;l=566

## SO or Reddit useful posts

- https://www.reddit.com/r/AndroidQuestions/comments/xgu8bd/what_is_dalvik/
- https://stackoverflow.com/questions/55970137/bypass-androids-hidden-api-restrictions
- https://stackoverflow.com/questions/31908205/what-exactly-does-androids-hide-annotation-do?noredirect=1&lq=1
- https://stackoverflow.com/questions/15417254/class-forname-throws-classnotfoundexception
- https://www.reddit.com/r/tasker/comments/i94rjj/using_the_java_function_action_to_get_raw_battery/
