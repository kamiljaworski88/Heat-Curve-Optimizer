# Heat Curve Optimizer — v0.1.0-beta (kandydat)

Status: kandydat do testów. Tag GitHub Release nie został jeszcze opublikowany.

## Funkcje
- Konfiguracja czujników w interfejsie Home Assistant.
- Rozdzielenie podłogówki i grzejników.
- Lokalna historia pomiarów i diagnostyka.
- Heurystyczna sugestia przesunięcia temperatury zasilania, bez sterowania pompą.
- Blokowanie sugestii przy konflikcie stref lub nieprawidłowych danych.
- Dashboard Lovelace w katalogu dashboard.
- Testy jednostkowe i symulacje awarii czujników w GitHub Actions.

## Znane ograniczenia
- Brak rzeczywistego wyznaczania nachylenia krzywej grzewczej.
- Nie jest automatycznie rozpoznawana praca klimatyzatorów i termostatów.
- Opcjonalne czujniki pompy nie są jeszcze wykorzystywane w rekomendacji.
- Dashboard wymaga dopasowania nazw encji i uzupełnienia kart pomieszczeń.
- Testy symulowane nie zastępują testu restartu działającego Home Assistant.

## Warunki publikacji wydania
- Potwierdzony zielony wynik testów CI.
- Udana instalacja z HACS i restart HA.
- Sprawdzenie zapisu historii oraz awarii i odzyskania czujników.

Instrukcja instalacji i diagnostyki: docs/INSTRUKCJA_PL.md.
