# Подсчёт метрик качества разрешения кореферентности

## Формат данных
Для корректности подсчёта данные должны находиться в __словаре__, ключами 
которого являются упоминания (в примере они обозначены как ```item1```, ```item2```,
 ```item3```), а значениями — множества цепочек, в которые эти упоминания входят:

```python
{
    "item1": set(["chain1", "chain2"]),
    "item2": set(["chain3"]),
    "item3": set(["chain1", "chain3"])
}
```
Порядок следования цепочек неважен.

## Используемые метрики

### MUC
> Vilain, M., Burger, J., Aberdeen, J., Connolly, D., and Hirschman, L. (1995, November). 
A model-theoretic coreference scoring scheme.
In _Proceedings of the 6th conference on Message understanding_ (pp. 45-52). 
Association for Computational Linguistics.

При использовании метрики MUC (самой первой появившейся метрике для подсчёта 
качества разрешения кореферентности) мы считаем для каждой цепочки, сколько упоминаний 
лишние, а сколько, наоборот, нужно добавить.

### B-Cubed
> Bagga, A., and Baldwin, B. (1998, May). Algorithms for scoring coreference chains. 
In _The first international conference on language resources and evaluation workshop 
on linguistics coreference_ (Vol. 1, pp. 563-566).

B-Cubed (иногда записывается как B^3) — следующая предложенная метрика. Для каждого 
упоминания она подсчитывает, в скольких цепочках оно определилось верно (т.е. 
присутствует в цепочкее)

### CEAF
> Luo, X. (2005, October). On coreference resolution performance metrics. 
In _Proceedings of the conference on Human Language Technology and Empirical 
Methods in Natural Language Processing_ (pp. 25-32). 
Association for Computational Linguistics.

Используя метрику CEAF, мы выравниваем реальные и выделенные сущности и после этого
начинаем расчёт. Мы обращаем внимание на отношение выровненных упоминаний ко всем 
имеющимся.