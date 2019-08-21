import pytest

from relcal.syntax.drc import DRCQueryLanguage


def test_all_followers_follow_someone__valid():
    content = '''
    Follows(a, b);

    {x: ALL[y](
            Friends(x, y) =>
            EXISTS[z](Friends(y, z))
        )
    }
    '''
    lang = DRCQueryLanguage()
    result = lang.transform(lang.parser.parse(content))


def test_all_followers_follow_someone__duplicated_field_name():
    content = '''
    Follows(a, a);

    {x: ALL[y](
            Friends(x, y) =>
            EXISTS[z](Friends(y, z))
        )
    }
    '''
    lang = DRCQueryLanguage()
    with pytest.raises(SyntaxError, match=r"duplicated field name"):
        lang.transform(lang.parser.parse(content))


def test_all_followers_follow_someone__duplicated_table_name():
    content = '''
    Follows(a, b);
    Follows(a, b, c);

    {x: ALL[y](
            Friends(x, y) =>
            EXISTS[z](Friends(y, z))
        )
    }
    '''
    lang = DRCQueryLanguage()
    with pytest.raises(SyntaxError, match=r"duplicated table name"):
        lang.transform(lang.parser.parse(content))


def test_all_followers_follow_someone__tuple_vars_overshadow():
    fst_content = '''
    Follows(a, b);

    {x: ALL[y](
            Friends(x, y) =>
            EXISTS[x](Friends(y, x))
        )
    }
    '''
    snd_content = '''
    Follows(a, b);

    {x: ALL[x](
            Friends(x, x) =>
            EXISTS[z](Friends(x, z))
        )
    }
    '''
    lang = DRCQueryLanguage()
    with pytest.raises(SyntaxError, match=r"variable name .* overshadowed"):
        lang.transform(lang.parser.parse(fst_content))
    with pytest.raises(SyntaxError, match=r"variable name .* overshadowed"):
        lang.transform(lang.parser.parse(snd_content))
