document.addEventListener('invalid', e => {
    e.preventDefault();
    return false;
}, true);

let validation = () => {
    let is_title_empty = $('#id_title').val().trim() === '';
    let is_not_selected = $('.dropdown-menu .active').length === 0;
    let is_content_empty = CKEDITOR.instances.content.getData() === '';
    let errorMessages = '';
    is_title_empty && (errorMessages += ", nhập tiêu đề");
    is_not_selected && (errorMessages += ", chọn chủ đề");
    is_content_empty && (errorMessages += ", nhập nội dung");
    if (errorMessages !== '') {
        event.preventDefault();
        errorMessages = errorMessages.substring(2);
        errorNotification({
            title: 'Lỗi',
            message: `Vui lòng ${errorMessages} bài viết`.replace(/,([^,]*)$/, ' và$1')
        });
    }
}
