# Лабораторна робота №2. Функції вищого порядку, lambda, композиція

**Варіант 4 — замовлення ресторану.** Конвеєр перетворень над списком замовлень
`{id, waiter, table, items}` без мутацій: сума чека (`map`), сервісний коефіцієнт для
столиків вибраної зони (`map`), відсікання малих чеків (`filter`), сортування за двома
ключами, Top-N (`islice`), reduce-агрегація `count / sum_checks / avg_check / max_check`.
Конвеєр збирається з однотипних кроків через `compose` / `pipe`.
Виконав: Данилюк Андрій Андрійович, ФЕП-23с. Перевірив: Свелеба Сергій Андрійович.

## Цілі

- описати запис через `TypedDict` і будувати нові записи замість зміни наявних;
- реалізувати трансформації як функції вищого порядку (`map`/`filter`/генератори, `lambda`);
- реалізувати `compose` і `pipe` та зібрати з них конвеєр;
- виконати сортування з двома ключами, Top-N і окрему `reduce`-агрегацію;
- перевірити Top-N, відсутність мутацій, агрегацію та композицію тестами; пройти black, ruff, mypy.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | Чисте ядро. `Item`, `Order`, `Stats` (`TypedDict`); `compose` / `pipe` (варіативні, через `reduce`), `compose2` (типізована композиція двох функцій), `identity`; трансформації-фабрики `with_check`, `boost_zone`, `min_check`, `normalize_waiters`, `sort_by_check_desc`, `take`; `make_zone_resolver` (столик → зона); `reduce_stats` і `revenue_by_waiter` (`reduce`); `build_pipeline`; розбір JSON-словників `parse_order` / `parse_item`. |
| `app.py` | Оболонка I/O: `argparse` (`--data`, `--top`, `--zone`, `--factor`, `--min-check`), читання `orders.json`, форматований друк Top-N, агрегатів і виторгу офіціантів. |
| `main.py` | Точка входу (викликає `app.main`). |
| `orders.json` | 12 замовлень: три зони столиків, малі та порожні чеки, однакові чеки для тай-брейка, імена офіціантів у різному регістрі. |
| `tests/test_core.py` | Кожна трансформація окремо, Top-N і тай-брейк за `id`, інша зона, немутація (`deepcopy`-знімок), `reduce_stats` (у т. ч. порожній вхід), `revenue_by_waiter`, `compose` == `pipe` у зворотному порядку, лінивість кроків, `parse_order` і відхилення некоректних даних. |
| `tests/test_properties.py` | Property-тести (Hypothesis): результат відсортований за `(-check, id)`, довжина ≤ N, усі чеки ≥ порога; вхід незмінний; коефіцієнт діє лише на зону; `reduce_stats` збігається з прямим обчисленням; `pipe(*fs) == compose(*reversed(fs))`. |
| `tests/test_app.py` | Читання файлу, аргументи CLI, формат рядків, повний вивід `main`. |
| `conftest.py` | Корінь лабораторної для імпортів у тестах; фікстура `orders`. |
| `report/Lab_02.docx` | Звіт. |

## Конвеєр (`build_pipeline`)

```python
pipe(
    normalize_waiters(),          # map:    "  OLENA " -> "Olena"
    with_check(),                 # map:    check = Σ price × qty
    boost_zone("terrace", 1.1),   # map:    check × 1.1 для столиків 11–20
    min_check(200.0),             # filter: check >= 200
    sort_by_check_desc(),         # sorted: key = (-check, id)
    take(3),                      # islice: Top-N
)
```

Кожен крок має тип `Step = Callable[[Iterable[Order]], Iterable[Order]]`, тому
`compose(*steps)` і `pipe(*steps)` — це просто `reduce(lambda acc, f: f(acc), steps, x)`.
Усі кроки ліниві (генератори, `map`, `filter`, `islice`), окрім `sorted`, який за визначенням
матеріалізує список; жоден не торкається вхідних словників — нові записи створюються
через `{**order, "check": ...}`, що підтверджено тестами з `deepcopy`-знімком і Hypothesis.

Зони столиків: `hall` 1–10, `terrace` 11–20, `vip` 21–30 (`make_zone_resolver` дозволяє
передати свою мапу). Агрегати: `reduce_stats` рахує `count`, `sum_checks`, `avg_check`,
`max_check` за один прохід `reduce` над кортежем-акумулятором; `revenue_by_waiter` будує
словник виторгу, створюючи на кожному кроці новий словник `{**acc, waiter: ...}`.

## Результат (`python app.py`)

```
orders: 12, zone 'terrace' x1.1, min check 200
top-3:
  #8  Bohdan   table 25 (vip    ) check   1300.00
  #5  Olena    table 22 (vip    ) check   1200.00
  #2  Taras    table 12 (terrace) check    858.00
stats (top): count=3 sum_checks=3358.00 avg_check=1119.33 max_check=1300.00
stats (all): count=12 sum_checks=6045.00 avg_check=503.75 max_check=1300.00
```

Замовлення №12 має такий самий чек 858.00, як і №2, але стоїть після нього — тай-брейк за `id`.

## Як запускати

```bash
pip install -r requirements.txt
python main.py
python app.py --top 2 --zone vip --factor 1.2 --min-check 300

pytest -q
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `Lab_02/`.
