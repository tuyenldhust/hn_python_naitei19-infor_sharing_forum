var editor = CKEDITOR.replace('content', {
    extraPlugins: 'notification'
});
// config CKEditor
CKEDITOR.config.height = 300;
CKEDITOR.config.width = 'auto';
CKEDITOR.config.toolbar = [
    ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
    ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
    ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
    ['Link', 'Unlink'],
    ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
    ['Format', 'Font', 'FontSize'],
    ['TextColor', 'BGColor'],
    ['Maximize', 'ShowBlocks', '-', 'Source']
];
// placeholder
CKEDITOR.config.editorplaceholder = 'Nội dung bài viết (*)';
// required
editor.on('required', function (evt) {
    editor.showNotification('Nội dung bài viết không được để trống', 'warning');
    evt.cancel();
});
