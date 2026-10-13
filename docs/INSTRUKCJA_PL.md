# Instrukcja PL — Heat Curve Optimizer beta

## Instalacja z GitHub przez HACS
1. Zrób kopię zapasową Home Assistant.
2. HACS → menu → Custom repositories / Niestandardowe repozytoria.
3. URL: https://github.com/kamiljaworski88/Heat-Curve-Optimizer; typ: Integration.
4. Zainstaluj Heat Curve Optimizer i uruchom ponownie Home Assistant.
5. Ustawienia → Urządzenia i usługi → Dodaj integrację → Heat Curve Optimizer.
6. Wybierz temperaturę zewnętrzną, docelową i czujniki pokojowe. Przypisz osobno pomieszczenia z podłogówką i grzejnikami.
7. Domyślnie zbieraj próbki co 5 minut i analizuj 24 godziny.

## Dashboard
Plik dashboard/heat_curve_optimizer.yaml to szablon do wklejenia w surowym edytorze dashboardu Lovelace. Wykorzystuje standardowe karty Home Assistant i układ sections, który adaptuje się do telefonu i tabletu.
Nazwy sensorów mogą się różnić po instalacji. Sprawdź je w Narzędzia deweloperskie → Stany i popraw YAML. Uzupełnij puste karty pomieszczeń swoimi encjami Aqara/Supla.

## Diagnostyka
- insufficient_data: za mało świeżych próbek; poczekaj na zapełnienie okna.
- invalid_data: brak encji, unavailable/unknown, nieprawidłowa liczba lub przekroczenie zakresu.
- zone_conflict: podłogówka i grzejniki mają sprzeczne potrzeby; sprawdź termostaty i przepływy.
- unstable_conditions: pogoda zmieniała się zbyt szybko.
- ready: wyłącznie wstępna sugestia przesunięcia temperatury, nie zmiana nachylenia krzywej.

## Bezpieczeństwo i prywatność
Nie podawaj tokenów Supla/Aqara/Atlantic. Integracja korzysta z istniejących encji Home Assistant. Historia próbek jest zapisywana lokalnie w .storage. Nie publikuj kopii zapasowych ani diagnostyki bez weryfikacji. Integracja nie steruje pompą.

## Znane ograniczenia beta
- Brak obliczania rzeczywistego nachylenia krzywej grzewczej.
- Nie uwzględnia jeszcze wpływu klimatyzatorów i termostatów pokojowych.
- Opcjonalne encje temperatury zasilania/powrotu, mocy i stanu pracy nie wpływają jeszcze na analizę.
- Nie wykrywa zamrożonych wartości czujnika na podstawie wieku ostatniej aktualizacji.
- Dashboard wymaga dopasowania identyfikatorów encji i uzupełnienia pomieszczeń.
- Testy symulowane nie zastępują restartu i instalacji na prawdziwym Home Assistant.
