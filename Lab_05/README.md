# Лабораторна робота №5. Ліниві обчислення: генератори та itertools

**Варіант 4 — геометрична прогресія.** Початкове значення `q0` і множник `r` задають
нескінченний лінивий потік `q0, q0·r, q0·r², ...` (власний генератор із `yield`). Значення
беруться до порогу через `takewhile`, накопичені сума й добуток рахуються через
`accumulate` без матеріалізації потоку.
Виконав: Данилюк Андрій Андрійович, ФЕП-23с. Перевірив: Свелеба Сергій Андрійович.

## Цілі

- generator expressions, `yield` / `yield from`, ітератори та лінивість;
- робота з нескінченними послідовностями (`fib_stream`, `naturals`, `geometric`);
- `itertools`: `islice`, `count`, `repeat`, `accumulate`, `takewhile`, `dropwhile`, `starmap`;
- універсальні `take` / `drop` / `sliding_window` та накопичення по потоку.

## Що зроблено

| Файл | Призначення |
|---|---|
| `streams.py` | Базове з методички: `fib_stream`, `naturals`, `take`, `drop`, `sliding_window` (на `deque(maxlen=k)`), `moving_average`, `window_sums` (`starmap`), обгортки `prefix_sums` / `prefix_products` (`accumulate`), `take_while` / `drop_while`. |
| `progression.py` | Варіант 4: нескінченний генератор `geometric(q0, r)`, альтернатива `geometric_accumulate` (`accumulate(repeat(r), mul, initial=q0)`), `up_to` / `above` (`takewhile` + захисний `islice` для `\|r\| <= 1`), `running_sums` / `running_products` (`accumulate`), формули `nth_term` і `closed_form_sum` для перевірки, `summarize_up_to` (NamedTuple `ProgressionSummary`) — один лінивий прохід. |
| `main.py` | Демо: Фібоначчі, вікна натуральних, рухоме середнє, прогресія до порогу, накопичені суми й добутки, спадна прогресія, підсумок. |
| `tests/test_fib_stream.py` | Перші 10 значень, `drop` + `take`, свіжий генератор на кожен виклик. |
| `tests/test_take_drop.py` | Просування спільного ітератора, `count`, `n = 0`, порожнє джерело, `n < 0`. |
| `tests/test_sliding_window.py` | Базові й граничні вікна (`k > len`, порожнє джерело, `k <= 0`), суми та рухоме середнє. |
| `tests/test_accumulate.py` | `accumulate` із сумою / добутком / `max`, `takewhile` / `dropwhile` на `count`. |
| `tests/test_progression.py` | Перші члени (зокрема `r < 0`, `q0 = 0`), дві реалізації збігаються, поріг, спадна прогресія, накопичені суми/добутки, формули, нескінченний випадок `r = 1` обмежено, некоректні аргументи, 3 property-тести Hypothesis. |
| `tests/test_laziness.py` | Ітератори-лічильники: обчислюється рівно стільки членів, скільки запитано (`take`, вікна, `up_to` зупиняється на першому члені понад поріг, `running_sums`). |
| `conftest.py` | Фікстура `doubling` (`q0 = 1`, `r = 2`). |
| `report/Lab_05.docx` | Звіт. |

## Лінивість і нескінченні потоки

Жодна функція ядра не викликає `list()` на вході: `geometric` обчислює наступний член лише
тоді, коли споживач просить значення, `up_to` зупиняється на першому члені понад поріг, а
`running_sums` / `running_products` — це `accumulate` над тим самим ітератором. Для `|r| <= 1`
прогресія може ніколи не перевищити поріг, тому `up_to` додатково обмежує потік `islice`
(`max_terms`). Єдина матеріалізація — `take` і `list(...)` на виході в `main.py` та тестах.

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `Lab_05/`.
