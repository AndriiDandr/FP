# Лабораторна робота №3. Нездатні до змін структури даних (immutability)

**Варіант 4 — склад товарів.** Сутності `Product` і `StockRecord`, теги як `frozenset`,
метадані постачальника як `MappingProxyType`. Pure-оновлення: поповнення залишку, зміна ціни,
додавання тегу; кожна операція повертає новий `StockRecord`. Один розрахунок (`stock_value`)
кешується через `lru_cache`.
Виконав: Данилюк Андрій Андрійович, ФЕП-23с. Перевірив: Свелеба Сергій Андрійович.

## Цілі

- застосувати `tuple`, `frozenset`, `@dataclass(frozen=True, slots=True)`, `MappingProxyType`;
- замінити мутації на повернення нових копій (`dataclasses.replace`, конкатенація tuple, `|` для frozenset);
- перевірити немутацію, read-only поведінку та хешованість тестами;
- виміряти ефект переходу на незмінну модель (`pytest --durations=5`).

## Що зроблено

| Файл | Призначення |
|---|---|
| `model.py` | `Product`, `StockRecord` (frozen, slots), `Tag = Literal[...]`, `make_meta` (proxy над копією), `make_record`. Методи `restock` / `change_price` / `add_tag` / `deactivate` повертають нові об'єкти через `replace`. |
| `core.py` | Чисті функції: `discount_factor`, `stock_value` (`@lru_cache`), pure-оновлення `restock`, `change_price`, `add_tag`, `with_supplier`, `recalculate`, `index_by_record` (запис як ключ словника), `freeze` (глибоке заморожування). |
| `mutable_model.py` | Мутабельна версія «до» (dict + list + set) — лише для порівняння часу. |
| `main.py` | Демонстрація: ланцюжок оновлень, незмінність оригіналу, кеш, read-only meta. |
| `tests/test_immutability.py` | Немутація, `FrozenInstanceError`, `TypeError` для proxy, копіювання джерела meta, хешованість і словник з ключем-записом, кеш `cache_info`, `freeze`, 2 property-тести (Hypothesis). |
| `tests/test_performance.py` | Два тести однакового навантаження на mutable- і immutable-моделі для `--durations=5`. |
| `conftest.py` | Фікстура `record`. |
| `report/Lab_03.docx` | Звіт. |

### Хешованість

`StockRecord` хешований завдяки `frozen=True`, але поле `supplier` (`mappingproxy`) не має
`__hash__`, тому воно виключене з хешу через `field(hash=False)` і бере участь лише у `__eq__`.
Усі інші поля (`Product`, `tuple`, `frozenset`, примітиви) хешуються.

## Порівняння часу (`python -m pytest -q --durations=5 -vv tests/test_performance.py`)

| Тест | Модель | Час |
|---|---|---|
| `test_mutable_before` | dict + list + set, вартість щоразу перераховується | ~0.05 s |
| `test_immutable_after` | frozen dataclass + tuple + `lru_cache` | ~0.01 s |

Незмінна модель на 2000 поповненнях створює 2000 нових tuple (O(n²) копіювання), але
кешований розрахунок вартості компенсує це: 1999 звернень із 2000 — cache hit.

## Висновок про незмінність

Переваги: референтна прозорість і прості тести без `deepcopy`, безпечне спільне читання,
хешованість (запис як ключ `dict`, вхід `lru_cache`). Накладні витрати: кожне оновлення
створює новий об'єкт і копіює tuple/frozenset, `MappingProxyType` захищає лише верхній рівень
(для вкладених структур потрібен `freeze`). Для складських записів ці витрати несуттєві,
а виграш у передбачуваності — великий.

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest -q --durations=5
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `Lab_03/`.
