-- Ce script crée les tables et insère toutes les données actuelles du projet .BJ

-- Supprime les tables si elles existent déjà pour garantir un départ à neuf.
-- ATTENTION : Ceci effacera les données existantes dans ces tables.

--CREATE DATABASE bimhackdb_groupe5;
--\connect bimhackdb_groupe5;
--\c bimhackdb_groupe5;

DROP TABLE IF EXISTS bj_kpis, bj_domain_history, bj_nameservers, bj_indicateurs_marche, bj_usage_plateformes, bj_qos_mesures;

-------------------------------------------
-- SECTION 1 : CRÉATION DES TABLES
-------------------------------------------

-- Table pour stocker les indicateurs clés quotidiens ou périodiques
CREATE TABLE IF NOT EXISTS bj_kpis (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    live_domain_count INTEGER,
    live_data_status VARCHAR(50),
    nameserver_count INTEGER,
    ipv6_availability_percent REAL,
    dnssec_status VARCHAR(50)
);

COMMENT ON TABLE bj_kpis IS 'Instantanés des indicateurs clés pour le ccTLD .BJ.';

-- Table pour stocker l'historique officiel du nombre de domaines
CREATE TABLE IF NOT EXISTS bj_domain_history (
    annee INTEGER PRIMARY KEY,
    nombre_domaines INTEGER NOT NULL,
    source VARCHAR(255)
);

COMMENT ON TABLE bj_domain_history IS 'Données officielles et sourcées de l''évolution du nombre de domaines .BJ.';

-- Table pour stocker les informations sur les serveurs de noms (NS)
CREATE TABLE IF NOT EXISTS bj_nameservers (
    id SERIAL PRIMARY KEY,
    last_updated_date DATE NOT NULL DEFAULT CURRENT_DATE,
    hostname VARCHAR(255) UNIQUE NOT NULL,
    ipv4_address VARCHAR(45),
    ipv6_address VARCHAR(45),
    country_code VARCHAR(10),
    asn_details TEXT
);

COMMENT ON TABLE bj_nameservers IS 'Informations techniques et de localisation des serveurs de noms du .BJ.';

-- Table pour stocker les indicateurs officiels du marché mobile et Internet (SIM, abonnés, pénétration, trafic)
CREATE TABLE IF NOT EXISTS bj_indicateurs_marche (
    annee INTEGER NOT NULL,
    indicateur VARCHAR(100) NOT NULL,
    operateur VARCHAR(20) NOT NULL DEFAULT 'Tous',
    valeur REAL NOT NULL,
    unite VARCHAR(50),
    variation_pct REAL,
    source VARCHAR(255),
    PRIMARY KEY (annee, indicateur, operateur)
);

COMMENT ON TABLE bj_indicateurs_marche IS 'Indicateurs officiels du marché des communications électroniques publiés par l''ARCEP BENIN (variation_pct : évolution annuelle en % indiquée par le rapport).';

-- Table pour stocker le nombre d'utilisateurs des plateformes numériques par opérateur et par genre
CREATE TABLE IF NOT EXISTS bj_usage_plateformes (
    annee INTEGER NOT NULL,
    operateur VARCHAR(20) NOT NULL,
    plateforme VARCHAR(50) NOT NULL,
    genre VARCHAR(10) NOT NULL,
    utilisateurs INTEGER NOT NULL,
    PRIMARY KEY (annee, operateur, plateforme, genre)
);

COMMENT ON TABLE bj_usage_plateformes IS 'Utilisateurs connectés aux plateformes (WhatsApp, Facebook, TikTok, Netflix) par opérateur et par genre.';

-- Table pour stocker les mesures quotidiennes de qualité de service (QoS) des réseaux mobiles
CREATE TABLE IF NOT EXISTS bj_qos_mesures (
    date_mesure DATE NOT NULL,
    operateur VARCHAR(20) NOT NULL,
    indicateur VARCHAR(100) NOT NULL,
    valeur REAL NOT NULL,
    unite VARCHAR(10),
    seuil REAL,
    PRIMARY KEY (date_mesure, operateur, indicateur)
);

COMMENT ON TABLE bj_qos_mesures IS 'Mesures de qualité de service (appels voix, débits 3G/4G) publiées par l''ARCEP BENIN, avec le seuil de conformité.';

-------------------------------------------
-- SECTION 2 : INSERTION DES DONNÉES
-------------------------------------------

-- Insertion des indicateurs clés actuels
INSERT INTO bj_kpis (snapshot_date, live_domain_count, live_data_status, nameserver_count, ipv6_availability_percent, dnssec_status)
VALUES
(CURRENT_DATE, 3382, 'estimation', 5, 60.0, 'Activé');

-- Insertion de l'historique officiel des domaines
-- Le rapport annuel 2025 de l'ARCEP ne publie pas le nombre de domaines .bj : l'année 2025 reste à compléter.
-- Utilise ON CONFLICT pour éviter les erreurs si une année existe déjà (met à jour les données)
INSERT INTO bj_domain_history (annee, nombre_domaines, source)
VALUES
(2019, 1624, 'Rapport Annuel ARCEP 2019'),
(2020, 1766, 'Rapport Annuel ARCEP 2020'),
(2021, 2690, 'Rapport Annuel ARCEP 2021'),
(2022, 3005, 'Rapport Annuel ARCEP 2022'),
(2023, 3447, 'Rapport Annuel ARCEP 2023'),
(2024, 3382, 'Rapport Annuel ARCEP 2024')
ON CONFLICT (annee) DO UPDATE SET
    nombre_domaines = EXCLUDED.nombre_domaines,
    source = EXCLUDED.source;

-- Insertion des informations sur les serveurs de noms
-- Utilise ON CONFLICT pour mettre à jour les entrées si un hostname existe déjà
INSERT INTO bj_nameservers (hostname, ipv4_address, ipv6_address, country_code, asn_details)
VALUES
('ns-bj.afrinic.net', '196.216.168.33', '2001:43f8:120::33', 'ZA', 'AS37177 (AFRINIC-ANYCAST, MU)'),
('ns-bj.nic.fr', '194.0.9.1', '2001:678:c::1', 'FR', 'AS2484 (NIC-FR-DNS-ANYCAST-AFNIC AFNIC Association Francaise pour le Nommage Internet en Cooperation, FR)'),
('ns1.nic.bj', '154.65.28.218', 'N/A', 'BJ', 'AS328098 (JENY-SAS-AS, BJ)'),
('ns2.nic.bj', '41.85.191.2', 'N/A', 'BJ', 'AS28683 (SBIN, BJ)'),
('pch.nic.bj', '204.61.216.125', '2001:500:14:6125:ad::1', 'US', 'AS42 (WOODYNET-1 - WoodyNet, Inc., US)')
ON CONFLICT (hostname) DO UPDATE SET
    ipv4_address = EXCLUDED.ipv4_address,
    ipv6_address = EXCLUDED.ipv6_address,
    country_code = EXCLUDED.country_code,
    asn_details = EXCLUDED.asn_details,
    last_updated_date = CURRENT_DATE;

-- Insertion des indicateurs officiels du marché (Rapport annuel d'activités 2025 de l'ARCEP, situation au 31/12/2025)
-- Opérateurs : MTN = SPACETEL BENIN, MOOV = MOOV AFRICA BENIN, CELTIIS = SBIN
INSERT INTO bj_indicateurs_marche (annee, indicateur, operateur, valeur, unite, variation_pct, source)
VALUES
(2024, 'Cartes SIM actives', 'Tous', 18.21, 'millions', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Cartes SIM actives', 'Tous', 18.17, 'millions', -0.2, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnés mobiles', 'Tous', 10328542, 'abonnés', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Pénétration mobile', 'Tous', 78.1, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Cartes SIM Internet mobile', 'Tous', 10.81, 'millions', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnés Internet mobile', 'Tous', 8594822, 'abonnés', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2024, 'Pénétration Internet mobile', 'Tous', 63.5, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Pénétration Internet mobile', 'Tous', 64.9, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2022, 'Abonnements Internet mobile 4G', 'Tous', 31, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnements Internet mobile 4G', 'Tous', 58, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnements Internet mobile 3G', 'Tous', 17, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnements Internet mobile 2G', 'Tous', 25, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2024, 'Trafic Internet mobile', 'Tous', 375.4, 'millions de Go', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Trafic Internet mobile', 'Tous', 551.6, 'millions de Go', 47, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Trafic voix mobile', 'Tous', 10.374, 'milliards de minutes', 51.57, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'SMS échangés', 'Tous', 603.188, 'millions', 39.5, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'ARPU mobile', 'Tous', 1622, 'FCFA par mois', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Chiffre d''affaires mobile', 'Tous', 350.02, 'milliards FCFA', 3.1, 'Rapport Annuel d''Activités ARCEP 2025'),
(2024, 'Part de marché (valeur)', 'CELTIIS', 16.3, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Part de marché (valeur)', 'MTN', 40.9, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Part de marché (valeur)', 'MOOV', 23.5, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Part de marché (valeur)', 'CELTIIS', 35.6, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnés Internet fixe', 'Tous', 105715, 'abonnés', 163.51, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Pénétration Internet fixe', 'Tous', 0.8, '%', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Abonnés téléphonie fixe', 'Tous', 78938, 'abonnés', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Fournisseurs d''accès à Internet', 'Tous', 27, 'FAI', NULL, 'Rapport Annuel d''Activités ARCEP 2025'),
(2025, 'Bande passante internationale', 'Tous', 350, 'Gbps', NULL, 'Rapport Annuel d''Activités ARCEP 2025')
ON CONFLICT (annee, indicateur, operateur) DO UPDATE SET
    valeur = EXCLUDED.valeur,
    unite = EXCLUDED.unite,
    variation_pct = EXCLUDED.variation_pct,
    source = EXCLUDED.source;

-- Insertion des utilisateurs des plateformes par opérateur et par genre (Tableau 8 du rapport 2025 ; CELTIIS non publié)
INSERT INTO bj_usage_plateformes (annee, operateur, plateforme, genre, utilisateurs)
VALUES
(2025, 'MTN', 'WhatsApp', 'Femme', 2240097),
(2025, 'MTN', 'WhatsApp', 'Homme', 3960491),
(2025, 'MTN', 'Facebook', 'Femme', 2602392),
(2025, 'MTN', 'Facebook', 'Homme', 4390852),
(2025, 'MTN', 'TikTok', 'Femme', 1575511),
(2025, 'MTN', 'TikTok', 'Homme', 2512204),
(2025, 'MTN', 'Netflix', 'Femme', 50393),
(2025, 'MTN', 'Netflix', 'Homme', 80153),
(2025, 'MOOV', 'WhatsApp', 'Femme', 850509),
(2025, 'MOOV', 'WhatsApp', 'Homme', 2391639),
(2025, 'MOOV', 'Facebook', 'Femme', 1181573),
(2025, 'MOOV', 'Facebook', 'Homme', 3413665)
ON CONFLICT (annee, operateur, plateforme, genre) DO UPDATE SET
    utilisateurs = EXCLUDED.utilisateurs;

-- Insertion des mesures de qualité de service (page "Qualité de service" d'arcep.bj, du 10/10/2026 au 16/10/2026)
INSERT INTO bj_qos_mesures (date_mesure, operateur, indicateur, valeur, unite, seuil)
VALUES
('2026-10-10', 'MTN', 'Taux de succès des appels voix', 99.5, '%', 99),
('2026-10-11', 'MTN', 'Taux de succès des appels voix', 99.56, '%', 99),
('2026-10-12', 'MTN', 'Taux de succès des appels voix', 99.56, '%', 99),
('2026-10-13', 'MTN', 'Taux de succès des appels voix', 99.56, '%', 99),
('2026-10-14', 'MTN', 'Taux de succès des appels voix', 99.57, '%', 99),
('2026-10-15', 'MTN', 'Taux de succès des appels voix', 99.58, '%', 99),
('2026-10-16', 'MTN', 'Taux de succès des appels voix', 99.56, '%', 99),
('2026-10-10', 'MOOV', 'Taux de succès des appels voix', 99.58, '%', 99),
('2026-10-11', 'MOOV', 'Taux de succès des appels voix', 99.56, '%', 99),
('2026-10-12', 'MOOV', 'Taux de succès des appels voix', 99.56, '%', 99),
('2026-10-13', 'MOOV', 'Taux de succès des appels voix', 99.57, '%', 99),
('2026-10-14', 'MOOV', 'Taux de succès des appels voix', 99.55, '%', 99),
('2026-10-15', 'MOOV', 'Taux de succès des appels voix', 99.27, '%', 99),
('2026-10-16', 'MOOV', 'Taux de succès des appels voix', 99.58, '%', 99),
('2026-10-10', 'CELTIIS', 'Taux de succès des appels voix', 99.47, '%', 99),
('2026-10-11', 'CELTIIS', 'Taux de succès des appels voix', 99.44, '%', 99),
('2026-10-12', 'CELTIIS', 'Taux de succès des appels voix', 99.38, '%', 99),
('2026-10-13', 'CELTIIS', 'Taux de succès des appels voix', 99.43, '%', 99),
('2026-10-14', 'CELTIIS', 'Taux de succès des appels voix', 99.45, '%', 99),
('2026-10-15', 'CELTIIS', 'Taux de succès des appels voix', 99.44, '%', 99),
('2026-10-16', 'CELTIIS', 'Taux de succès des appels voix', 99.32, '%', 99),
('2026-10-10', 'MTN', 'Taux de blocage des appels voix', 0.08, '%', 1),
('2026-10-11', 'MTN', 'Taux de blocage des appels voix', 0.07, '%', 1),
('2026-10-12', 'MTN', 'Taux de blocage des appels voix', 0.06, '%', 1),
('2026-10-13', 'MTN', 'Taux de blocage des appels voix', 0.06, '%', 1),
('2026-10-14', 'MTN', 'Taux de blocage des appels voix', 0.05, '%', 1),
('2026-10-15', 'MTN', 'Taux de blocage des appels voix', 0.05, '%', 1),
('2026-10-16', 'MTN', 'Taux de blocage des appels voix', 0.05, '%', 1),
('2026-10-10', 'MOOV', 'Taux de blocage des appels voix', 0, '%', 1),
('2026-10-11', 'MOOV', 'Taux de blocage des appels voix', 0, '%', 1),
('2026-10-12', 'MOOV', 'Taux de blocage des appels voix', 0, '%', 1),
('2026-10-13', 'MOOV', 'Taux de blocage des appels voix', 0.01, '%', 1),
('2026-10-14', 'MOOV', 'Taux de blocage des appels voix', 0, '%', 1),
('2026-10-15', 'MOOV', 'Taux de blocage des appels voix', 0, '%', 1),
('2026-10-16', 'MOOV', 'Taux de blocage des appels voix', 0, '%', 1),
('2026-10-10', 'CELTIIS', 'Taux de blocage des appels voix', 0.02, '%', 1),
('2026-10-11', 'CELTIIS', 'Taux de blocage des appels voix', 0.02, '%', 1),
('2026-10-12', 'CELTIIS', 'Taux de blocage des appels voix', 0.03, '%', 1),
('2026-10-13', 'CELTIIS', 'Taux de blocage des appels voix', 0.04, '%', 1),
('2026-10-14', 'CELTIIS', 'Taux de blocage des appels voix', 0.03, '%', 1),
('2026-10-15', 'CELTIIS', 'Taux de blocage des appels voix', 0.02, '%', 1),
('2026-10-16', 'CELTIIS', 'Taux de blocage des appels voix', 0.03, '%', 1),
('2026-10-10', 'MTN', 'Débit descendant 3G', 1488.11, 'kbps', 450),
('2026-10-11', 'MTN', 'Débit descendant 3G', 1555.42, 'kbps', 450),
('2026-10-12', 'MTN', 'Débit descendant 3G', 1534.55, 'kbps', 450),
('2026-10-13', 'MTN', 'Débit descendant 3G', 1538.46, 'kbps', 450),
('2026-10-14', 'MTN', 'Débit descendant 3G', 1546.12, 'kbps', 450),
('2026-10-15', 'MTN', 'Débit descendant 3G', 1563.7, 'kbps', 450),
('2026-10-16', 'MTN', 'Débit descendant 3G', 1552.43, 'kbps', 450),
('2026-10-10', 'MOOV', 'Débit descendant 3G', 1083.99, 'kbps', 450),
('2026-10-11', 'MOOV', 'Débit descendant 3G', 1102.53, 'kbps', 450),
('2026-10-12', 'MOOV', 'Débit descendant 3G', 1103.96, 'kbps', 450),
('2026-10-13', 'MOOV', 'Débit descendant 3G', 1116.49, 'kbps', 450),
('2026-10-14', 'MOOV', 'Débit descendant 3G', 1104.76, 'kbps', 450),
('2026-10-15', 'MOOV', 'Débit descendant 3G', 1121.03, 'kbps', 450),
('2026-10-16', 'MOOV', 'Débit descendant 3G', 1089.55, 'kbps', 450),
('2026-10-10', 'CELTIIS', 'Débit descendant 3G', 1708.46, 'kbps', 450),
('2026-10-11', 'CELTIIS', 'Débit descendant 3G', 1703.53, 'kbps', 450),
('2026-10-12', 'CELTIIS', 'Débit descendant 3G', 1719.29, 'kbps', 450),
('2026-10-13', 'CELTIIS', 'Débit descendant 3G', 1697.22, 'kbps', 450),
('2026-10-14', 'CELTIIS', 'Débit descendant 3G', 1712.78, 'kbps', 450),
('2026-10-15', 'CELTIIS', 'Débit descendant 3G', 1739.71, 'kbps', 450),
('2026-10-16', 'CELTIIS', 'Débit descendant 3G', 1751.99, 'kbps', 450),
('2026-10-10', 'MTN', 'Débit montant 3G', 98.29, 'kbps', 70),
('2026-10-11', 'MTN', 'Débit montant 3G', 104.5, 'kbps', 70),
('2026-10-12', 'MTN', 'Débit montant 3G', 103.04, 'kbps', 70),
('2026-10-13', 'MTN', 'Débit montant 3G', 103.05, 'kbps', 70),
('2026-10-14', 'MTN', 'Débit montant 3G', 101.68, 'kbps', 70),
('2026-10-15', 'MTN', 'Débit montant 3G', 101.13, 'kbps', 70),
('2026-10-16', 'MTN', 'Débit montant 3G', 100.71, 'kbps', 70),
('2026-10-10', 'MOOV', 'Débit montant 3G', 99.12, 'kbps', 70),
('2026-10-11', 'MOOV', 'Débit montant 3G', 101, 'kbps', 70),
('2026-10-12', 'MOOV', 'Débit montant 3G', 101.03, 'kbps', 70),
('2026-10-13', 'MOOV', 'Débit montant 3G', 100.48, 'kbps', 70),
('2026-10-14', 'MOOV', 'Débit montant 3G', 99.32, 'kbps', 70),
('2026-10-15', 'MOOV', 'Débit montant 3G', 101.9, 'kbps', 70),
('2026-10-16', 'MOOV', 'Débit montant 3G', 98.86, 'kbps', 70),
('2026-10-10', 'CELTIIS', 'Débit montant 3G', 127.85, 'kbps', 70),
('2026-10-11', 'CELTIIS', 'Débit montant 3G', 131.34, 'kbps', 70),
('2026-10-12', 'CELTIIS', 'Débit montant 3G', 129.72, 'kbps', 70),
('2026-10-13', 'CELTIIS', 'Débit montant 3G', 140.03, 'kbps', 70),
('2026-10-14', 'CELTIIS', 'Débit montant 3G', 127.97, 'kbps', 70),
('2026-10-15', 'CELTIIS', 'Débit montant 3G', 129.07, 'kbps', 70),
('2026-10-16', 'CELTIIS', 'Débit montant 3G', 128.89, 'kbps', 70),
('2026-10-10', 'MTN', 'Débit descendant 4G', 17.42, 'Mbps', 5),
('2026-10-11', 'MTN', 'Débit descendant 4G', 17.73, 'Mbps', 5),
('2026-10-12', 'MTN', 'Débit descendant 4G', 17.56, 'Mbps', 5),
('2026-10-13', 'MTN', 'Débit descendant 4G', 17.59, 'Mbps', 5),
('2026-10-14', 'MTN', 'Débit descendant 4G', 17.58, 'Mbps', 5),
('2026-10-15', 'MTN', 'Débit descendant 4G', 17.53, 'Mbps', 5),
('2026-10-16', 'MTN', 'Débit descendant 4G', 17.55, 'Mbps', 5),
('2026-10-10', 'MOOV', 'Débit descendant 4G', 17.36, 'Mbps', 5),
('2026-10-11', 'MOOV', 'Débit descendant 4G', 17.53, 'Mbps', 5),
('2026-10-12', 'MOOV', 'Débit descendant 4G', 17.37, 'Mbps', 5),
('2026-10-13', 'MOOV', 'Débit descendant 4G', 17.42, 'Mbps', 5),
('2026-10-14', 'MOOV', 'Débit descendant 4G', 17.51, 'Mbps', 5),
('2026-10-15', 'MOOV', 'Débit descendant 4G', 17.35, 'Mbps', 5),
('2026-10-16', 'MOOV', 'Débit descendant 4G', 17.25, 'Mbps', 5),
('2026-10-10', 'CELTIIS', 'Débit descendant 4G', 19.19, 'Mbps', 5),
('2026-10-11', 'CELTIIS', 'Débit descendant 4G', 19.19, 'Mbps', 5),
('2026-10-12', 'CELTIIS', 'Débit descendant 4G', 19.3, 'Mbps', 5),
('2026-10-13', 'CELTIIS', 'Débit descendant 4G', 19.1, 'Mbps', 5),
('2026-10-14', 'CELTIIS', 'Débit descendant 4G', 19.22, 'Mbps', 5),
('2026-10-15', 'CELTIIS', 'Débit descendant 4G', 19.39, 'Mbps', 5),
('2026-10-16', 'CELTIIS', 'Débit descendant 4G', 19.43, 'Mbps', 5),
('2026-10-10', 'MTN', 'Débit montant 4G', 3.04, 'Mbps', 2),
('2026-10-11', 'MTN', 'Débit montant 4G', 3.14, 'Mbps', 2),
('2026-10-12', 'MTN', 'Débit montant 4G', 3.07, 'Mbps', 2),
('2026-10-13', 'MTN', 'Débit montant 4G', 3.07, 'Mbps', 2),
('2026-10-14', 'MTN', 'Débit montant 4G', 3.06, 'Mbps', 2),
('2026-10-15', 'MTN', 'Débit montant 4G', 3.07, 'Mbps', 2),
('2026-10-16', 'MTN', 'Débit montant 4G', 3.06, 'Mbps', 2),
('2026-10-10', 'MOOV', 'Débit montant 4G', 2.45, 'Mbps', 2),
('2026-10-11', 'MOOV', 'Débit montant 4G', 2.51, 'Mbps', 2),
('2026-10-12', 'MOOV', 'Débit montant 4G', 2.49, 'Mbps', 2),
('2026-10-13', 'MOOV', 'Débit montant 4G', 2.48, 'Mbps', 2),
('2026-10-14', 'MOOV', 'Débit montant 4G', 2.48, 'Mbps', 2),
('2026-10-15', 'MOOV', 'Débit montant 4G', 2.5, 'Mbps', 2),
('2026-10-16', 'MOOV', 'Débit montant 4G', 2.47, 'Mbps', 2),
('2026-10-10', 'CELTIIS', 'Débit montant 4G', 3.59, 'Mbps', 2),
('2026-10-11', 'CELTIIS', 'Débit montant 4G', 3.64, 'Mbps', 2),
('2026-10-12', 'CELTIIS', 'Débit montant 4G', 3.61, 'Mbps', 2),
('2026-10-13', 'CELTIIS', 'Débit montant 4G', 3.56, 'Mbps', 2),
('2026-10-14', 'CELTIIS', 'Débit montant 4G', 3.57, 'Mbps', 2),
('2026-10-15', 'CELTIIS', 'Débit montant 4G', 3.59, 'Mbps', 2),
('2026-10-16', 'CELTIIS', 'Débit montant 4G', 3.57, 'Mbps', 2)
ON CONFLICT (date_mesure, operateur, indicateur) DO UPDATE SET
    valeur = EXCLUDED.valeur,
    unite = EXCLUDED.unite,
    seuil = EXCLUDED.seuil;

-- Fin du script
SELECT 'Base de données créée et remplie avec succès !' AS status;