const react = async (id, type) => {
    let res = await fetch(`/post/${id}/react/${type}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    let data = await res.json()
    if (res.status === 200) {
       $('#feedback_value').html(data.total_feedback_value)
        let upvote = $('#upvote-btn')
        let downvote = $('#downvote-btn')
        if (data.message === 'upvote') {
            upvote.addClass('react-choice')
            downvote.removeClass('react-choice')
        } else if (data.message === 'downvote') {
            upvote.removeClass('react-choice')
            downvote.addClass('react-choice')
        } else if (data.message === 'deleted') {
            upvote.removeClass('react-choice')
            downvote.removeClass('react-choice')
        }
    } else {
        errorNotification({
            title: 'Lỗi',
            message: 'Bạn cần đăng nhập',
        });
    }
}

const bookmark = async (id) => {
    let res = await fetch(`/post/${id}/bookmark`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    let data = await res.json()
    if (res.status === 200) {
        let bookmark = $('.bookmark-btn')
        if (data.message === 'bookmarked') {
            bookmark.addClass('fa-solid').removeClass('fa-regular')
                .children().text('Đã lưu')
        } else if (data.message === 'deleted') {
            bookmark.removeClass('fa-solid').addClass('fa-regular')
            .children().text('Lưu')
        }
    } else {
        errorNotification({
            title: 'Lỗi',
            message: 'Bạn cần đăng nhập',
        });
    }
}
