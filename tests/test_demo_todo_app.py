import pytest
import re
from playwright.sync_api import Page, expect

TODO_ITEMS = [
    'buy some cheese',
    'feed the cat',
    'book a doctors appointment'
]

@pytest.fixture(autouse=True, scope='function')
def before_each(page: Page):
    page.goto('/todomvc')

def create_default_todos(page: Page):
    new_todo = page.get_by_placeholder('What needs to be done?')
    for item in TODO_ITEMS:
        new_todo.fill(item)
        new_todo.press('Enter')

def check_number_of_todos_in_local_storage(page: Page, expected: int):
    return page.wait_for_function("e => JSON.parse(localStorage['react-todos']).length === e", arg=expected)

def check_number_of_completed_todos_in_local_storage(page: Page, expected: int):
    return page.wait_for_function("e => JSON.parse(localStorage['react-todos']).filter(todo => todo.completed).length === e", arg=expected)

def check_todos_in_local_storage(page: Page, title: str):
    return page.wait_for_function("(t) => JSON.parse(localStorage['react-todos']).map(todo => todo.title).includes(t)", arg=title)

@pytest.mark.describe('New Todo')
class TestNewTodo:

    @pytest.mark.it('should allow me to add todo items')
    def test_should_allow_me_to_add_todo_items(self, page: Page):
        new_todo = page.get_by_placeholder('What needs to be done?')
        new_todo.fill(TODO_ITEMS[0])
        new_todo.press('Enter')
        expect(page.get_by_test_id('todo-title')).to_have_text([TODO_ITEMS[0]])
        new_todo.fill(TODO_ITEMS[1])
        new_todo.press('Enter')
        expect(page.get_by_test_id('todo-title')).to_have_text([TODO_ITEMS[0], TODO_ITEMS[1]])
        check_number_of_todos_in_local_storage(page, 2)

    @pytest.mark.it('should clear text input field when an item is added')
    def test_should_clear_text_input_field_when_an_item_is_added(self, page: Page):
        new_todo = page.get_by_placeholder('What needs to be done?')
        new_todo.fill(TODO_ITEMS[0])
        new_todo.press('Enter')
        expect(new_todo).to_be_empty()
        check_number_of_todos_in_local_storage(page, 1)

    @pytest.mark.it('should append new items to the bottom of the list')
    def test_should_append_new_items_to_the_bottom_of_the_list(self, page: Page):
        create_default_todos(page)
        todo_count = page.get_by_test_id('todo-count')
        expect(page.get_by_text('3 items left')).to_be_visible()
        expect(todo_count).to_have_text('3 items left')
        expect(todo_count).to_contain_text('3')
        expect(todo_count).to_have_text(re.compile('3'))
        expect(page.get_by_test_id('todo-title')).to_have_text(TODO_ITEMS)
        check_number_of_todos_in_local_storage(page, 3)

@pytest.mark.describe('Mark all as completed')
class TestMarkAllAsCompleted:

    @pytest.fixture(autouse=True)
    def before_each_mark_all(self, page: Page):
        create_default_todos(page)
        check_number_of_todos_in_local_storage(page, 3)

    @pytest.mark.it('should allow me to mark all items as completed')
    def test_should_allow_me_to_mark_all_items_as_completed(self, page: Page):
        page.get_by_label('Mark all as complete').check()
        expect(page.get_by_test_id('todo-item')).to_have_class(['completed', 'completed', 'completed'])
        check_number_of_completed_todos_in_local_storage(page, 3)

    @pytest.mark.it('should allow me to clear the complete state of all items')
    def test_should_allow_me_to_clear_the_complete_state_of_all_items(self, page: Page):
        toggle_all = page.get_by_label('Mark all as complete')
        toggle_all.check()
        toggle_all.uncheck()
        expect(page.get_by_test_id('todo-item')).to_have_class(['', '', ''])

    @pytest.mark.it('complete all checkbox should update state when items are completed / cleared')
    def test_complete_all_checkbox_should_update_state_when_items_are_completed_cleared(self, page: Page):
        toggle_all = page.get_by_label('Mark all as complete')
        toggle_all.check()
        expect(toggle_all).to_be_checked()
        check_number_of_completed_todos_in_local_storage(page, 3)
        first_todo = page.get_by_test_id('todo-item').nth(0)
        first_todo.get_by_role('checkbox').uncheck()
        expect(toggle_all).not_to_be_checked()
        first_todo.get_by_role('checkbox').check()
        check_number_of_completed_todos_in_local_storage(page, 3)
        expect(toggle_all).to_be_checked()

@pytest.mark.describe('Item')
class TestItem:

    @pytest.mark.it('should allow me to mark items as complete')
    def test_should_allow_me_to_mark_items_as_complete(self, page: Page):
        new_todo = page.get_by_placeholder('What needs to be done?')
        for item in TODO_ITEMS[:2]:
            new_todo.fill(item)
            new_todo.press('Enter')
        first_todo = page.get_by_test_id('todo-item').nth(0)
        first_todo.get_by_role('checkbox').check()
        expect(first_todo).to_have_class('completed')
        second_todo = page.get_by_test_id('todo-item').nth(1)
        expect(second_todo).not_to_have_class('completed')
        second_todo.get_by_role('checkbox').check()
        expect(first_todo).to_have_class('completed')
        expect(second_todo).to_have_class('completed')

    @pytest.mark.it('should allow me to un-mark items as complete')
    def test_should_allow_me_to_un_mark_items_as_complete(self, page: Page):
        new_todo = page.get_by_placeholder('What needs to be done?')
        for item in TODO_ITEMS[:2]:
            new_todo.fill(item)
            new_todo.press('Enter')
        first_todo = page.get_by_test_id('todo-item').nth(0)
        second_todo = page.get_by_test_id('todo-item').nth(1)
        first_todo_checkbox = first_todo.get_by_role('checkbox')
        first_todo_checkbox.check()
        expect(first_todo).to_have_class('completed')
        expect(second_todo).not_to_have_class('completed')
        check_number_of_completed_todos_in_local_storage(page, 1)
        first_todo_checkbox.uncheck()
        expect(first_todo).not_to_have_class('completed')
        expect(second_todo).not_to_have_class('completed')
        check_number_of_completed_todos_in_local_storage(page, 0)

    @pytest.mark.it('should allow me to edit an item')
    def test_should_allow_me_to_edit_an_item(self, page: Page):
        create_default_todos(page)
        todo_items = page.get_by_test_id('todo-item')
        second_todo = todo_items.nth(1)
        second_todo.dblclick()
        expect(second_todo.get_by_role('textbox', name='Edit')).to_have_value(TODO_ITEMS[1])
        second_todo.get_by_role('textbox', name='Edit').fill('buy some sausages')
        second_todo.get_by_role('textbox', name='Edit').press('Enter')
        expect(todo_items).to_have_text([TODO_ITEMS[0], 'buy some sausages', TODO_ITEMS[2]])
        check_todos_in_local_storage(page, 'buy some sausages')

@pytest.mark.describe('Editing')
class TestEditing:

    @pytest.fixture(autouse=True)
    def before_each_editing(self, page: Page):
        create_default_todos(page)
        check_number_of_todos_in_local_storage(page, 3)

    @pytest.mark.it('should hide other controls when editing')
    def test_should_hide_other_controls_when_editing(self, page: Page):
        todo_item = page.get_by_test_id('todo-item').nth(1)
        todo_item.dblclick()
        expect(todo_item.get_by_role('checkbox')).not_to_be_visible()
        expect(todo_item.locator('label', has_text=TODO_ITEMS[1])).not_to_be_visible()
        check_number_of_todos_in_local_storage(page, 3)

    @pytest.mark.it('should save edits on blur')
    def test_should_save_edits_on_blur(self, page: Page):
        todo_items = page.get_by_test_id('todo-item')
        todo_items.nth(1).dblclick()
        todo_items.nth(1).get_by_role('textbox', name='Edit').fill('buy some sausages')
        todo_items.nth(1).get_by_role('textbox', name='Edit').dispatch_event('blur')
        expect(todo_items).to_have_text([TODO_ITEMS[0], 'buy some sausages', TODO_ITEMS[2]])
        check_todos_in_local_storage(page, 'buy some sausages')

    @pytest.mark.it('should trim entered text')
    def test_should_trim_entered_text(self, page: Page):
        todo_items = page.get_by_test_id('todo-item')
        todo_items.nth(1).dblclick()
        todo_items.nth(1).get_by_role('textbox', name='Edit').fill('    buy some sausages    ')
        todo_items.nth(1).get_by_role('textbox', name='Edit').press('Enter')
        expect(todo_items).to_have_text([TODO_ITEMS[0], 'buy some sausages', TODO_ITEMS[2]])
        check_todos_in_local_storage(page, 'buy some sausages')

    @pytest.mark.it('should remove the item if an empty text string was entered')
    def test_should_remove_the_item_if_an_empty_text_string_was_entered(self, page: Page):
        todo_items = page.get_by_test_id('todo-item')
        todo_items.nth(1).dblclick()
        todo_items.nth(1).get_by_role('textbox', name='Edit').fill('')
        todo_items.nth(1).get_by_role('textbox', name='Edit').press('Enter')
        expect(todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[2]])

    @pytest.mark.it('should cancel edits on escape')
    def test_should_cancel_edits_on_escape(self, page: Page):
        todo_items = page.get_by_test_id('todo-item')
        todo_items.nth(1).dblclick()
        todo_items.nth(1).get_by_role('textbox', name='Edit').fill('buy some sausages')
        todo_items.nth(1).get_by_role('textbox', name='Edit').press('Escape')
        expect(todo_items).to_have_text(TODO_ITEMS)

@pytest.mark.describe('Counter')
class TestCounter:

    @pytest.mark.it('should display the current number of todo items')
    def test_should_display_the_current_number_of_todo_items(self, page: Page):
        new_todo = page.get_by_placeholder('What needs to be done?')
        todo_count = page.get_by_test_id('todo-count')
        new_todo.fill(TODO_ITEMS[0])
        new_todo.press('Enter')
        expect(todo_count).to_contain_text('1')
        new_todo.fill(TODO_ITEMS[1])
        new_todo.press('Enter')
        expect(todo_count).to_contain_text('2')
        check_number_of_todos_in_local_storage(page, 2)

@pytest.mark.describe('Clear completed button')
class TestClearCompletedButton:

    @pytest.fixture(autouse=True)
    def before_each_clear_completed(self, page: Page):
        create_default_todos(page)

    @pytest.mark.it('should display the correct text')
    def test_should_display_the_correct_text(self, page: Page):
        page.locator('.todo-list li .toggle').first.check()
        expect(page.get_by_role('button', name='Clear completed')).to_be_visible()

    @pytest.mark.it('should remove completed items when clicked')
    def test_should_remove_completed_items_when_clicked(self, page: Page):
        todo_items = page.get_by_test_id('todo-item')
        todo_items.nth(1).get_by_role('checkbox').check()
        page.get_by_role('button', name='Clear completed').click()
        expect(todo_items).to_have_count(2)
        expect(todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[2]])

    @pytest.mark.it('should be hidden when there are no items that are completed')
    def test_should_be_hidden_when_there_are_no_items_that_are_completed(self, page: Page):
        page.locator('.todo-list li .toggle').first.check()
        page.get_by_role('button', name='Clear completed').click()
        expect(page.get_by_role('button', name='Clear completed')).to_be_hidden()

@pytest.mark.describe('Persistence')
class TestPersistence:

    @pytest.mark.it('should persist its data')
    def test_should_persist_its_data(self, page: Page):
        new_todo = page.get_by_placeholder('What needs to be done?')
        for item in TODO_ITEMS[:2]:
            new_todo.fill(item)
            new_todo.press('Enter')
        todo_items = page.get_by_test_id('todo-item')
        first_todo_check = todo_items.nth(0).get_by_role('checkbox')
        first_todo_check.check()
        expect(todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[1]])
        expect(first_todo_check).to_be_checked()
        expect(todo_items).to_have_class(['completed', ''])
        check_number_of_completed_todos_in_local_storage(page, 1)
        page.reload()
        expect(todo_items).to_have_text([TODO_ITEMS[0], TODO_ITEMS[1]])
        expect(first_todo_check).to_be_checked()
        expect(todo_items).to_have_class(['completed', ''])

@pytest.mark.describe('Routing')
class TestRouting:

    @pytest.fixture(autouse=True)
    def before_each_routing(self, page: Page):
        create_default_todos(page)
        check_todos_in_local_storage(page, TODO_ITEMS[0])

    @pytest.mark.it('should allow me to display active items')
    def test_should_allow_me_to_display_active_items(self, page: Page):
        todo_item = page.get_by_test_id('todo-item')
        page.get_by_test_id('todo-item').nth(1).get_by_role('checkbox').check()
        check_number_of_completed_todos_in_local_storage(page, 1)
        page.get_by_role('link', name='Active').click()
        expect(todo_item).to_have_count(2)
        expect(todo_item).to_have_text([TODO_ITEMS[0], TODO_ITEMS[2]])

    @pytest.mark.it('should respect the back button')
    def test_should_respect_the_back_button(self, page: Page):
        todo_item = page.get_by_test_id('todo-item')
        page.get_by_test_id('todo-item').nth(1).get_by_role('checkbox').check()
        check_number_of_completed_todos_in_local_storage(page, 1)
        page.get_by_role('link', name='All').click()
        expect(todo_item).to_have_count(3)
        page.get_by_role('link', name='Active').click()
        page.get_by_role('link', name='Completed').click()
        expect(todo_item).to_have_count(1)
        page.go_back()
        expect(todo_item).to_have_count(2)
        page.go_back()
        expect(todo_item).to_have_count(3)

    @pytest.mark.it('should allow me to display completed items')
    def test_should_allow_me_to_display_completed_items(self, page: Page):
        page.get_by_test_id('todo-item').nth(1).get_by_role('checkbox').check()
        check_number_of_completed_todos_in_local_storage(page, 1)
        page.get_by_role('link', name='Completed').click()
        expect(page.get_by_test_id('todo-item')).to_have_count(1)

    @pytest.mark.it('should allow me to display all items')
    def test_should_allow_me_to_display_all_items(self, page: Page):
        page.get_by_test_id('todo-item').nth(1).get_by_role('checkbox').check()
        check_number_of_completed_todos_in_local_storage(page, 1)
        page.get_by_role('link', name='Active').click()
        page.get_by_role('link', name='Completed').click()
        page.get_by_role('link', name='All').click()
        expect(page.get_by_test_id('todo-item')).to_have_count(3)

    @pytest.mark.it('should highlight the currently applied filter')
    def test_should_highlight_the_currently_applied_filter(self, page: Page):
        expect(page.get_by_role('link', name='All')).to_have_class('selected')
        active_link = page.get_by_role('link', name='Active')
        completed_link = page.get_by_role('link', name='Completed')
        active_link.click()
        expect(active_link).to_have_class('selected')
        completed_link.click()
        expect(completed_link).to_have_class('selected')
