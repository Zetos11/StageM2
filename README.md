# Semaine 1

J'ai récupéré le matériel que j'utilisais déjà au cours de mon PFE, je n'ai donc pas eu besoin de beaucoup de temps d'installation et de configuration.
J'ai repris le projet là où je l'avais laissé, j'étais en train de chercher à trouver un moyen d'interagir avec le BatteryManager pour obtenir une mesure précise de la batterie restante sur l'appareil (J'obtenais une mesure en pourcentage de batterie restante seulement). J'ai fini par comprendre que la documention officielle Android était erronée, les valeurs censées être retourner par certains appels ne correspondaient pas. J'ai donc expérimenté avec toute les méthodes et appels disponibles et j'ai fini par trouver le bon appel. L'appel à *BATTERY_PROPERTY_CHARGE_COUNTER* était censé fournir la capacité totale de la batterie en microampère-heure mais fourni à la place le résultat de l'appel *BATTERY_PROPERTY_ENERGY_COUNTER*. Cet appel qui renvoie une erreur quand on le teste, est censé renvoyer la batterie restante en microampère.

![Not working](https://github.com/Zetos11/StageM2/blob/main/Figures/Screenshot_20240408-132435.webp?raw=true)

La suite des opérations est logique, maintenant qu'on a une mesure relativement précise de la batterie et qu'on peut faire des suppositions quand à la consommation d'une application sur un certain laps de temps, on continue de chercher à obtenir une meilleure granularitée, si possible en pouvant récupérer le consommation des composants du téléphone (Caméra, GPS, CPU, Ecran, etc.).
