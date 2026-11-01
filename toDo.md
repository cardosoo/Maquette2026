# Ajout des fonctions RD
Je voudrais ajouter le service RH à ce service déjà existant.
- il y a 2 sous-services à ajouter. 
    - Le premier concerne la définition des modification de service dû (MSD). C'est un service annualisé donc on doit lui passer l'année comme paramètre et il renvoie quelque chose qui ressemble à cela (c'est un extrait).
```json 
[
    {'code': 'AMENAG', 'intitule': 'Aménagement de service enseignants 2e degré', 'info': {'Libelle Multiplicateur': -1}},
    {'code': 'CONG_MAL', 'intitule': 'Congé maladie', 'info': {'Libelle Multiplicateur': -1}},
    {'code': 'AMENAG_PREV', 'intitule': 'Aménagement service suite à préconisation Médecine du travail - 2/3 du service statutaire MAX', 'info': {'Libelle Multiplicateur': -1}},
    {'code': 'ARRIVE', 'intitule': 'Arrivé en cours d'année', 'info': {'Libelle Multiplicateur': -1}},
] 
```
    Il faudra pouvoir le mettre à jour à partir de données qui ressembleront à cela : 
```text
Code    Libelle Multiplicateur  Pas d'heures complémentaires
AMENAG	Aménagement de service enseignants 2e degré	-1	
AMENAG_PREV	Aménagement service suite à préconisation Médecine du travail - 2/3 du service statutaire MAX	-1	
ARRIVE	Arrivé en cours d'année	-1	
```
    - le deuxième concerne les fonctions du référentiel (REF). C'est égelement un service annualisé donc on doit pouvoir lui passer l'année comme paramètre et il renvoie quelque chose qui ressembleà à cela (c'est un extrait)
```json
    {'code': 'ANIM_STRUCTU', 'intitule': 'Animation de structures de dialogue science-société', 'Libelle court': 'Animation structures dialogue' 'info': {'Domaine Fonctionnel': 'D103 - Form init&cont doct', 'Formation à préciser': 'Peut dans serv.', 'oui'}},
    {'code': 'CONCEPT-EAD-FOAD', 'intitule': 'Conception et développement de modules d'EAD ou de FOAD', 'Libelle court': 'Conception et développement de modules d'EAD ou de FOAD' 'info': {'Domaine Fonctionnel': 'D103 - Form init&cont doct', 'Formation à préciser': 'Peut dans serv.', 'oui'}},
```
    Il faudrait pouvoir le mettre à jour à partir de données qui ressembleront à cela :
```text
Code    Libelle Libelle court Domaine Fonctionnel Structure Formation à préciser Peut dans serv.
ANIM_STRUCTU	Animation de structures de dialogue science-société	Animation structures dialogue	D103 - Form init&cont doct			Oui
CONCEPT-EAD-FOAD	Conception et développement de modules d'EAD ou de FOAD	Conception et développement de modules d'EAD ou de FOAD	D115 - Pilotage et support			Oui
```

