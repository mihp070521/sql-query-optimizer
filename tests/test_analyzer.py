import pytest
from optimizer.analyzer import QueryAnalyzer


@pytest.fixture
def analyzer():
    return QueryAnalyzer()


def test_select_star_detected(analyzer):
    issues = analyzer.analyze("SELECT * FROM users")
    rules = [i.rule for i in issues]
    assert "select-star" in rules


def test_missing_limit_detected(analyzer):
    issues = analyzer.analyze("SELECT id FROM users WHERE active = true")
    rules = [i.rule for i in issues]
    assert "missing-limit" in rules


def test_limit_not_flagged(analyzer):
    issues = analyzer.analyze("SELECT id FROM users LIMIT 10")
    rules = [i.rule for i in issues]
    assert "missing-limit" not in rules


def test_like_prefix_wildcard(analyzer):
    issues = analyzer.analyze("SELECT id FROM users WHERE name LIKE '%john%'")
    rules = [i.rule for i in issues]
    assert "like-prefix-wildcard" in rules


def test_function_on_column(analyzer):
    issues = analyzer.analyze("SELECT id FROM users WHERE UPPER(name) = 'JOHN'")
    rules = [i.rule for i in issues]
    assert "function-on-indexed-column" in rules


def test_implicit_join(analyzer):
    issues = analyzer.analyze("SELECT u.id, o.total FROM users u, orders o WHERE u.id = o.user_id")
    rules = [i.rule for i in issues]
    assert "implicit-join" in rules


def test_clean_query_no_issues(analyzer):
    issues = analyzer.analyze("SELECT id, name FROM users WHERE active = true LIMIT 10")
    assert len(issues) == 0


def test_multiple_issues(analyzer):
    sql = "SELECT * FROM users WHERE UPPER(name) = 'JOHN' OR status = 'active'"
    issues = analyzer.analyze(sql)
    rules = {i.rule for i in issues}
    assert "select-star" in rules
    assert "function-on-indexed-column" in rules
