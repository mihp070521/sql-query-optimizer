# sql-query-optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Analyze SQL queries for common performance issues and get optimization suggestions.

## Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `select-star` | Medium | SELECT * retrieves unnecessary columns |
| `missing-limit` | Low | No LIMIT clause on SELECT |
| `missing-where` | Low | Full table scan without WHERE |
| `like-prefix-wildcard` | High | Leading % in LIKE prevents index use |
| `not-in-subquery` | Medium | NOT IN with subquery is slow |
| `or-in-where` | Medium | OR in WHERE may prevent index use |
| `function-on-indexed-column` | High | Function on column prevents index |
| `implicit-join` | High | Comma-separated FROM is error-prone |

## Quick Start

```python
from optimizer import QueryAnalyzer

analyzer = QueryAnalyzer()
issues = analyzer.analyze("SELECT * FROM users WHERE UPPER(name) = 'JOHN'")

for issue in issues:
    print(f"[{issue.severity}] {issue.rule}: {issue.suggestion}")
```

## License

[MIT](LICENSE)
