# Instrukcja PL — Heat Curve Optimizer beta

## Instalacja i aktualizacja przez HACS
1. Wykonaj kopię zapasową Home Assistant.
2. HACS → Niestandardowe repozytoria → dodaj repo jako Integration.
3. Zainstaluj lub zaktualizuj integrację, uruchom ponownie Home Assistant.
4. Ustawienia → Urządzenia i usługi → Heat Curve Optimizer: sprawdź czujniki temperatury zewnętrznej, docelowej oraz pomieszczeń.
5. W Narzędzia deweloperskie → Stany sprawdź nowe `switch.data_collection` i istniejące encje czujników.
6. **Po aktualizacji ze starego schematu przełącznik jest OFF.** Stara historia jest jednorazowo odrzucana.
7. Włącz **Zbieranie danych** dopiero wtedy, gdy CO naprawdę działa. Wyłącz przy zakończeniu sezonu lub ogrzewaniu wyłącznie klimatyzacją.
8. Przy ponownym OFF/ON nowa historia nie jest kasowana; próbki spoza okna analizy są usuwane przy kolejnym zbieraniu.

## Dashboard
`dashboard/heat_curve_optimizer.yaml` jest pełnym przykładem dashboardu (surowy YAML całego dashboardu z `title:` i `views:`).
Używa encji zaobserwowanych w instalacji: `sensor.recommendation`, `sensor.temperature_error`, `sensor.confidence`, `sensor.data_coverage`, `sensor.data_quality`, `sensor.diagnostic_reason`.
Nowy przełącznik najprawdopodobniej otrzyma `switch.data_collection`. **Identyfikatory nie są gwarantowane**: sprawdź je w Narzędzia deweloperskie → Stany i w razie potrzeby zamień w YAML.
Do edytora pojedynczego widoku wklej tylko element z `views`, nie całe `title/views`.
Karty stref pokazują średnie dopiero po udanej analizie; czujniki indywidualnych pomieszczeń dodaj w UI dashboardu.

## Diagnostyka
- `paused`: przełącznik wyłączony; próbki nie są dodawane.
- `insufficient_data`: mniej niż 70% poprawnych próbek w oknie; dla 24 h / 5 min zwykle co najmniej około 17 h zbierania.
- `invalid_data`: brak, `unavailable`, `unknown` lub nieprawidłowa wartość.
- `zone_conflict`: sprzeczne potrzeby stref; sprawdź termostaty i przepływy.
- `unstable_conditions`: nadmierna zmienność temperatury zewnętrznej.
- `ready`: wyłącznie wstępna sugestia przesunięcia, nie zmiana nachylenia.

## Bezpieczeństwo i ograniczenia
Integracja nie steruje pompą ciepła. Próbki zapisuje lokalnie w `.storage`. Nie publikuj tokenów ani danych z domowej instalacji.
Opcjonalne czujniki pracy pompy, zasilania/powrotu i mocy nie wpływają jeszcze na rekomendację.
Nie wykrywa zamrożonych odczytów na podstawie wieku aktualizacji; nie modeluje klimatyzacji ani zamkniętych siłowników.
Testy jednostkowe i GitHub Actions nie zastępują testu restartu na prawdziwym Home Assistant.
