# Heat Curve Optimizer — instrukcja PL (v0.9.2)

## 1. Instalacja / aktualizacja przez HACS

1. Wykonaj kopię zapasową Home Assistant.
2. Wejdź w **HACS → Niestandardowe repozytoria**.
3. Dodaj repozytorium jako **Integration**:
   `https://github.com/kamiljaworski88/Heat-Curve-Optimizer`
4. Zainstaluj lub zaktualizuj integrację.
5. **Uruchom ponownie Home Assistant.**
6. Ustawienia → Urządzenia i usługi → dodaj/skonfiguruj **Heat Curve Optimizer**.
7. Wybierz temperaturę zewnętrzną, temperaturę docelową oraz czujniki pomieszczeń podłogówki i/lub grzejników.
8. Opcjonalnie dodaj temperaturę zasilania, powrotu oraz encje termostatów/zaworów.
9. Włącz **Data collection / Zbieranie danych**, gdy CO rzeczywiście pracuje.

## 2. FastMile Dashboard v2 — zalecany wygląd

Od v0.9.2 karta JavaScript jest dostarczana razem z integracją HACS. **Nie trzeba kopiować pliku JS do /config/www.**

Po restarcie Home Assistant dodaj na dashboardzie kartę **Ręcznie** i wklej:

```yaml
type: custom:heat-curve-fastmile-card
applied_button: button.i_applied_the_recommendation
```

Jeżeli przycisk otrzymał inny identyfikator, sprawdź go w **Narzędzia deweloperskie → Stany** i zmień `applied_button`.

Karta JS jest udostępniana przez integrację pod adresem:

```text
/heat_curve_optimizer/heat-curve-fastmile-card.js
```

Dodaj ten adres jeden raz jako zasób Lovelace typu **JavaScript Module** w Ustawienia → Pulpity → Zasoby. Jeśli zasobami zarządzasz przez YAML, dodaj go do sekcji `resources`.

### Widoki karty

FastMile Dashboard v2 ma własną nawigację:

- **Przegląd** — status, rekomendacja, pokrycie/pewność i wizualizacja temperatur;
- **Pomieszczenia** — analiza poszczególnych pomieszczeń;
- **Nauka budynku** — czas reakcji, profil temperaturowy i wniosek slope/offset;
- **Instalacja** — zasilanie, powrót i ΔT.

## 3. Pozostałe dashboardy

- `dashboard/heat_curve_optimizer.yaml` — pełny dashboard Lovelace;
- `dashboard/heat_curve_optimizer_widget.yaml` — kompaktowy widget;
- `dashboard/heat_curve_fastmile.yaml` — minimalny przykład FastMile JS.

## 4. Jak czytać diagnostykę

- `paused` — zbieranie danych wyłączone;
- `insufficient_data` — za mało poprawnych próbek;
- `invalid_data` — brak lub błędna wartość;
- `zone_conflict` — podłogówka i grzejniki mają sprzeczne potrzeby;
- `local_room_issue` — pojedyncze pomieszczenie odstaje; najpierw sprawdź zawór, termostat i przepływ;
- `controls_blocking` — stany termostatów/zaworów powodują, że strojenie wspólnej krzywej byłoby niewiarygodne;
- `unstable_conditions` — warunki zewnętrzne są zbyt zmienne;
- `ready` — warunki pozwalają na rekomendację.

## 5. Nachylenie czy przesunięcie?

Po zebraniu danych w różnych zakresach temperatury zewnętrznej integracja buduje profil domu. Przykładowo:

- podobne niedogrzanie zarówno przy łagodnej, jak i zimnej pogodzie → bardziej prawdopodobne podniesienie **offsetu**;
- poprawnie przy cieplejszej pogodzie, niedogrzanie przy mrozie → bardziej prawdopodobne zwiększenie **nachylenia**;
- poprawnie przy mrozie, przegrzewanie w cieplejsze dni → wskazanie dotyczące **nachylenia**, a nie prostego obniżania całej krzywej.

To nadal wskazówka. Integracja nie zmienia ustawień pompy.

## 6. „Zastosowałem rekomendację”

Przycisk służy wyłącznie do poinformowania algorytmu, że faktycznie zastosowałeś aktualną rekomendację. Od tego momentu integracja może porównywać zachowanie domu po zmianie w podobnych warunkach pogodowych.

## 7. Bezpieczeństwo

Heat Curve Optimizer pozostaje doradcą **read-only**. Nie steruje pompą ciepła i nie zmienia krzywej automatycznie. Dane są przechowywane lokalnie. Diagnostyka ΔT i hydrauliki ma charakter obserwacyjny i nie zastępuje pomiarów instalatora.

Po aktualizacji zawsze sprawdź logi Home Assistant oraz działanie encji po restarcie. Zielone testy GitHub Actions nie zastępują testu na rzeczywistej instalacji.
