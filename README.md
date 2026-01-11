# Blender Conveyor Belt Simulation

Symulacja taśmy produkcyjnej w Blenderze 5.0 z automatycznym renderowaniem obrazów przy każdej pozycji ruchu taśmy.

## Specyfikacja

- **Taśma**: 2m x 0.6m x 0.02m
- **Boxy**: 0.1m x 0.1m x 0.1m, losowo rozmieszczone, różne kolory
- **Kamera**: Wysokość 1.5m, 640x480px, pokrywa całą szerokość taśmy
- **Oświetlenie**: Listwa pod kątem 45° nad taśmą
- **Ruch**: Skoki co 0.02m (100 pozycji na całej długości)
- **Render**: Jeden obraz na każdą pozycję taśmy

## Struktura Projektu

```
Blender_conveyer/
├── scripts/
│   ├── main.py              # Główny skrypt uruchamiający symulację
│   ├── scene_setup.py       # Tworzenie taśmy i boxów
│   ├── camera_config.py     # Konfiguracja kamery i renderowania
│   ├── lighting_setup.py    # Oświetlenie sceny
│   └── render_manager.py    # System renderowania sekwencji
├── config/
│   └── conveyor_config.json # Konfiguracja parametrów
├── renders/                 # Wygenerowane obrazy (tworzone automatycznie)
└── README.md
```

## Instalacja i Uruchomienie

### Wymagania
- Blender 5.0 lub nowszy
- Python 3.11+ (wbudowany w Blendera)

### Metoda 1: Tryb tekstowy (Headless)

Renderowanie w tle bez GUI:

```bash
blender --background --python scripts/main.py
```

### Metoda 2: W Blenderze (GUI) - NAJPROSTSZA

**Sposób A: Używając pomocniczego skryptu (zalecane)**

1. Otwórz Blender 5.0
2. Przejdź do zakładki **Scripting**
3. Otwórz plik `scripts/run_in_blender.py` (Text → Open)
4. **WAŻNE**: Upewnij się, że ścieżka `PROJECT_DIR` w linii 12 jest poprawna
5. Kliknij **Run Script** (▶) lub naciśnij `Alt+P`

**Sposób B: Bezpośrednie uruchomienie main.py**

1. Najpierw zapisz pusty plik .blend w głównym folderze projektu: `File → Save As → Conveyer_v1.blend`
2. Przejdź do zakładki **Scripting**
3. Otwórz plik `scripts/main.py` (Text → Open)
4. Kliknij **Run Script** lub naciśnij `Alt+P`

### Metoda 3: Import i uruchomienie w konsoli Pythona

W konsoli Blendera (Scripting → Python Console):

```python
import sys
sys.path.insert(0, r"D:\Github\Blender_conveyer\scripts")

import main
main.main(render=False)  # render=False = tylko setup bez renderowania
```

## Konfiguracja

Edytuj plik `config/conveyor_config.json` aby dostosować parametry:

### Taśma
```json
"conveyor": {
  "length": 2.0,        // Długość taśmy (m)
  "width": 0.6,         // Szerokość taśmy (m)
  "thickness": 0.02,    // Grubość taśmy (m)
  "step_size": 0.02     // Wielkość kroku ruchu (m)
}
```

### Boxy
```json
"boxes": {
  "size": 0.1,              // Rozmiar kostki (m)
  "min_count": 5,           // Minimalna liczba boxów
  "max_count": 15,          // Maksymalna liczba boxów
  "z_layer_offset": 0.0001, // Offset wysokości między boxami (m) - zapobiega artefaktom
  "random_seed": null,      // Seed dla losowości (null = losowy)
  "random_colors": true     // Czy używać różnych kolorów
}
```

**Uwaga o nakładaniu boxów:** Boxy mogą się nakładać losowo. Każdy kolejny box jest umieszczany
minimalnie wyżej (o `z_layer_offset`), dzięki czemu w miejscu przecięcia nowszy box przykrywa
starszy. To zapobiega artefaktom renderowania ("czarnym dziurom") przy nakładaniu się obiektów.

### Kamera
```json
"camera": {
  "height": 1.5,        // Wysokość kamery nad taśmą (m)
  "resolution_x": 640,  // Szerokość obrazu (px)
  "resolution_y": 480   // Wysokość obrazu (px)
}
```

### Oświetlenie
```json
"lighting": {
  "type": "area",                // Typ światła
  "angle_degrees": 45,           // Kąt nachylenia (stopnie)
  "distance_from_conveyor": 1.0, // Odległość od taśmy (m)
  "strength": 100,               // Moc światła (W)
  "size": 2.0,                   // Rozmiar listwy (m)
  "use_fill_light": false        // Dodatkowe światło wypełniające
}
```

**Uwaga o `use_fill_light`:**
- `false` (domyślnie) - **Zalecane dla symulacji przemysłowej**
  - Tylko jedno główne światło pod kątem 45°
  - Realistyczne cienie i kontrasty
  - Symulacja rzeczywistych warunków systemu wizyjnego
- `true` - Dodaje słabsze światło z przeciwnej strony
  - Łagodniejsze cienie
  - Lepiej dla wizualizacji/prezentacji
  - **NIE zalecane dla testowania algorytmów wizyjnych**

### Renderowanie
```json
"render": {
  "output_folder": "renders",  // Folder wyjściowy
  "file_format": "PNG",        // Format (PNG, JPEG, etc.)
  "engine": "CYCLES",          // Silnik (CYCLES lub EEVEE)
  "samples": 64,               // Liczba próbek (jakość)
  "use_denoising": true        // Czy używać denoising
}
```

## Opcje Uruchamiania

### Tylko setup bez renderowania
```bash
blender --background --python scripts/main.py -- --no-render
```

### Z podglądem animacji (wymaga GUI)
```python
import main
main.main(render=False, preview=True)
```

## Wyjście

Renderowane obrazy są zapisywane w folderze `renders/` jako:
- `frame_0001.png` - pierwsza pozycja taśmy
- `frame_0002.png` - druga pozycja
- ...
- `frame_0100.png` - ostatnia pozycja

Każdy obraz to widok z kamery na aktualny fragment taśmy z boxami.

## Jak działa nakładanie boxów?

System pozwala na losowe nakładanie się boxów, co jest bardziej realistyczne dla symulacji
taśmy produkcyjnej. Aby zapobiec artefaktom renderowania (Z-fighting, "czarne dziury"),
każdy kolejny box jest umieszczany minimalnie wyżej:

- Box #0: wysokość = base_z
- Box #1: wysokość = base_z + 0.0001m
- Box #2: wysokość = base_z + 0.0002m
- itd.

Różnica jest mikroskopyjna (0.1mm), więc wizualnie wszystkie boxy wydają się na tym samym
poziomie, ale silnik renderowania wie, który jest "na wierzchu" w miejscu przecięcia.

**Zalety tego podejścia:**
- ✅ Brak "czarnych dziur" przy nakładaniu
- ✅ Bardziej realistyczna symulacja (rzeczywiste obiekty też mogą się nakładać)
- ✅ Wszystkie boxy zawsze mogą być umieszczone (brak ograniczeń przestrzennych)
- ✅ Prostsza implementacja i szybsze wykonanie

## Dostosowywanie

### Zmiana liczby boxów
W `config/conveyor_config.json` ustaw:
```json
"min_count": 10,
"max_count": 20
```

### Zmiana jakości renderowania
```json
"samples": 128,           // Więcej próbek = lepsza jakość, dłuższy czas
"use_denoising": true
```

### Zmiana silnika renderowania
```json
"engine": "EEVEE"         // Szybszy, ale mniej fotorealistyczny
```

### Powtarzalne rozmieszczenie boxów
```json
"random_seed": 42         // Ta sama liczba = te same pozycje boxów
```

### Włączenie światła wypełniającego (NIE dla symulacji przemysłowej!)
```json
"use_fill_light": true    // Dodaje dodatkowe światło (tylko do wizualizacji)
```
**Uwaga:** Pozostaw `false` jeśli testujesz algorytmy wizyjne - chcesz realistycznych warunków!

## Struktura Animacji

- **Frame 1**: Taśma na pozycji 0m (początek)
- **Frame 2**: Taśma przesunięta o 0.02m
- **Frame 3**: Taśma przesunięta o 0.04m
- ...
- **Frame 100**: Taśma przesunięta o 1.98m (koniec)

Każda klatka = jedna pozycja renderowania.

## Troubleshooting

### Błąd "No module named 'scene_setup'" lub podobne
Ten błąd występuje gdy Blender nie może znaleźć modułów projektu. Rozwiązania:

**Rozwiązanie 1 (najlepsze):** Użyj skryptu `run_in_blender.py`:
- Otwórz plik `scripts/run_in_blender.py` w Text Editorze Blendera
- Upewnij się, że ścieżka `PROJECT_DIR` w linii 12 wskazuje na Twój katalog projektu
- Uruchom skrypt (Alt+P)

**Rozwiązanie 2:** Zapisz plik .blend w głównym folderze projektu:
- File → Save As → `Conveyer_v1.blend` (w folderze `D:\Github\Blender_conveyer\`)
- Następnie uruchom `main.py` z Text Editora

**Rozwiązanie 3:** Ręczne ustawienie ścieżki w konsoli:
```python
import sys
sys.path.insert(0, r"D:\Github\Blender_conveyer\scripts")  # Zmień na swoją ścieżkę!
```
Następnie uruchom skrypt.

### GPU nie jest używane
W `camera_config.py:66-68` zmień `CUDA` na `OPENCL` lub `METAL` w zależności od karty graficznej.

### Zbyt długi czas renderowania
- Zmniejsz `samples` w konfiguracji (np. do 32)
- Użyj silnika `EEVEE` zamiast `CYCLES`
- Zmniejsz rozdzielczość kamery

### Boxy nakładają się i powstają artefakty ("czarna dziura")
**Problem został naprawiony!** System używa warstwowania Z - każdy kolejny box jest umieszczany
minimalnie wyżej, więc w miejscu nakładania nowszy box jest widoczny na wierzchu.

Jeśli nadal widzisz artefakty, zwiększ offset wysokości w `config/conveyor_config.json`:
```json
"z_layer_offset": 0.0002  // Zwiększ jeśli wciąż są problemy (domyślnie 0.0001m)
```

### Za dużo/za mało boxów na taśmie
Dostosuj w konfiguracji:
```json
"min_count": 10,  // Minimum
"max_count": 20   // Maximum
```

### Boxy wypadają poza taśmę
System automatycznie oblicza bezpieczne granice. Jeśli problem występuje, sprawdź rozmiary w konfiguracji.

## Przydatne Polecenia

### Sprawdzenie wersji Blendera
```bash
blender --version
```

### Renderowanie tylko jednej klatki (test)
W konsoli Blendera:
```python
import render_manager
render_manager.render_single_position(config, position_index=0)
```

### Export sceny do .blend
Po uruchomieniu skryptu:
```python
import bpy
bpy.ops.wm.save_as_mainfile(filepath="D:/Github/Blender_conveyer/conveyor_scene.blend")
```

## Licencja

Projekt open-source do użytku edukacyjnego i komercyjnego.
