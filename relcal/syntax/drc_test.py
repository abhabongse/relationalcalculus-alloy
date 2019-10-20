import pytest

from relcal.syntax.drc import DRCQueryLanguage

lang = DRCQueryLanguage()


@pytest.mark.parametrize('content', [
    pytest.param('''
        Follows(a, b);
    
        {x: ALL[y](
                Friends(x, y) =>
                EXISTS[z](Friends(y, z))
            )
        }
    ''', id='all_followers_follow_someone'),
])
def test_transform_valid(content):
    # TODO: use result of transformation for validation
    lang.transform(lang.parser.parse(content))


@pytest.mark.parametrize('content', [
    pytest.param('''
        Follows(a, a);
    
        {x: ALL[y](
                Friends(x, y) =>
                EXISTS[z](Friends(y, z))
            )
        }
    ''', id='a-a'),
])
def test_duplicated_field_name(content):
    with pytest.raises(SyntaxError, match=r"duplicated field name"):
        lang.transform(lang.parser.parse(content))


@pytest.mark.parametrize('content', [
    pytest.param('''
        Follows(a, b);
        Follows(a, b, c);
    
        {x: ALL[y](
                Friends(x, y) =>
                EXISTS[z](Friends(y, z))
            )
        }
    ''', id='Follows-Follows'),
])
def test_duplicated_table_name(content):
    with pytest.raises(SyntaxError, match=r"duplicated table name"):
        lang.transform(lang.parser.parse(content))


@pytest.mark.parametrize('content', [
    pytest.param('''
        Follows(a, b);
    
        {x: ALL[y](
                Friends(x, y) =>
                EXISTS[x](Friends(y, x))
            )
        }
    ''', id='tuple_vars-outer_pred'),
    pytest.param('''
        Follows(a, b);
    
        {x: ALL[x](
                Friends(x, x) =>
                EXISTS[z](Friends(x, z))
            )
        }
    ''', id='tuple_vars-inner_pred'),
    pytest.param('''
        Follows(a, b);
    
        {x: ALL[y](
                Friends(x, y) =>
                EXISTS[y](Friends(x, y))
            )
        }
    ''', id='outer_pred-inner_pred'),
])
def test_tuple_vars_overshadow(content):
    with pytest.raises(SyntaxError, match=r"variable name .* overshadowed"):
        lang.transform(lang.parser.parse(content))


@pytest.mark.parametrize('content', [
    pytest.param('''
        Follows(a, b);
    
        {x: ALL[y](
                Friends(x, y) =>
                EXISTS[z](Friends(x, w))
            )
        }
    ''', id='w'),
])
def test_free_variable(content):
    with pytest.raises(SyntaxError, match=r"free variable name .*"):
        lang.transform(lang.parser.parse(content))
