function show(selector) {
  $(selector).removeClass('hidden');
}

function hide(selector) {
  $(selector).addClass('hidden');
}

function showQuestion(options) {
  hide(options.acrossClears);
  show(options.acrossQuestions);
  hide(options.allContainer);
}

function showClear(options) {
  show(options.acrossClears);
  hide(options.acrossQuestions);
  $(options.actionContainer).removeClass(options.selectedClass);
  show(options.allContainer);
  hide(options.counterContainer);
}

function reset(options) {
  hide(options.acrossClears);
  hide(options.acrossQuestions);
  hide(options.allContainer);
  show(options.counterContainer);
}

function clearAcross(options) {
  reset(options);
  $(options.acrossInput).val(0);
  $(options.actionContainer).removeClass(options.selectedClass);
}

function checker(actionCheckboxes, options, checked) {
  if (checked) {
      showQuestion(options);
  } else {
      reset(options);
  }
  $(actionCheckboxes).prop('checked', checked);
  $(actionCheckboxes).closest('tr').toggleClass(options.selectedClass, checked);
}

function updateCounter(actionCheckboxes, options) {
  const sel = $(actionCheckboxes).filter(':checked').length;
  const counter = $(options.counterContainer);
  // data-actions-icnt is defined in the generated HTML
  // and contains the total amount of objects in the queryset
  const actions_icnt = Number(counter.attr('data-actions-icnt'));
  counter.text(sel + " của " + actions_icnt + " được chọn");

  const allToggle = $(options.allToggleId);
  allToggle.prop('checked', sel === actionCheckboxes.length);
  if (allToggle.prop('checked')) {
      showQuestion(options);
  }
  else {
      clearAcross(options);
  }
}

const defaults = {
  actionContainer: "#changelist-form > div.actions",
  counterContainer: "#changelist-form > div.actions > span.action-counter",
  allContainer: "#changelist-form > div.actions > span.all",
  acrossQuestions: "#changelist-form > div.actions > span.question",
  acrossClears: "#changelist-form > div.actions > span.clear",
  allToggleId: "#action-toggle",
  selectedClass: "selected",
  acrossInput: "#changelist-form > div.actions > input",
};

window.Actions = (actionCheckboxes) => {
  const options = defaults;
  let list_editable_changed = false;
  let lastChecked = null;
  let shiftPressed = false;

  $(document).on('keyup keydown', (event) => {
    shiftPressed = event.shiftKey;
  });



  $(options.allToggleId).on('click', function(event) {
    checker(actionCheckboxes, options, this.checked);
    updateCounter(actionCheckboxes, options);
  });

  $(options.acrossQuestions + " a").on('click', function(event) {
    event.preventDefault();
    const acrossInputs = $(options.acrossInput);
    acrossInputs.val(1);
    showClear(options);
  });

  $(options.acrossClears + " a").on('click', function(event) {
    event.preventDefault();
    $(options.allToggleId).prop('checked', false);
    clearAcross(options);
    checker(actionCheckboxes, options, false);
    updateCounter(actionCheckboxes, options);
  });

  function affectedCheckboxes(target, withModifier) {
    const multiSelect = (lastChecked && withModifier && lastChecked !== target);
    if (!multiSelect) {
        return [target];
    }

    const checkboxes = $('.action-select');
    const targetIndex = checkboxes.index(target);
    const lastCheckedIndex = checkboxes.index(lastChecked);
    const startIndex = Math.min(targetIndex, lastCheckedIndex);
    const endIndex = Math.max(targetIndex, lastCheckedIndex);
    const filtered = checkboxes.filter((index) => (startIndex <= index) && (index <= endIndex));
    return filtered;
  }

  $('#dtHorizontal tbody').on('change', function(event) {
    const target = event.target;
    if ($(target).hasClass('action-select')) {
        const checkboxes = affectedCheckboxes(target, shiftPressed);
        checker(checkboxes, options, target.checked);
        updateCounter(actionCheckboxes, options);
        lastChecked = target;
    } else {
        list_editable_changed = true;
    }
  });

  $('#changelist-form > div.actions.mt-2 > button.btn.btn-danger').on('click', function(event) {
    if (list_editable_changed) {
        const confirmed = confirm("Bạn có những thay đổi chưa được lưu trên các trường có thể chỉnh sửa riêng lẻ. Nếu bạn thực hiện một hành động, những thay đổi chưa lưu của bạn sẽ bị mất.");
        if (!confirmed) {
            event.preventDefault();
        }
    }
  });

  const el = $('#changelist-form input[name=_save]');
  if (el) {
    el.on('click', function(event) {
      if (document.querySelector('[name=action]').value) {
        const text = list_editable_changed
          ? "Bạn đã chọn một hành động, nhưng bạn chưa lưu các thay đổi của mình thành các trường riêng lẻ. Vui lòng nhấp vào OK để lưu. Bạn sẽ cần phải chạy lại hành động."
          : "Bạn đã chọn một hành động, và bạn chưa thực hiện bất kỳ thay đổi nào trên các trường riêng lẻ. Bạn có thể đang tìm kiếm nút Đi chứ không phải nút Lưu.";
        if (!confirm(text)) {
          event.preventDefault();
        }
      }
    });
  }

  $(window).on('pageshow', function(event) {
    if (event.originalEvent.persisted) {
      updateCounter(actionCheckboxes, options);
    }
  });
}

$(document).ready(function() {
  const actionsEls = $('tr input.action-select');
  
  if (actionsEls.length > 0) {
    Actions(actionsEls);
  }
});

