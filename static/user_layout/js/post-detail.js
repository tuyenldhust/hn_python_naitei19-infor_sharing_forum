const react = async (id, type) => {
    let res = await fetch(`/post/${id}/react/${type}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    let data = await res.json()
    if (res.status === 200) {
        let feedback_value = document.getElementById(`feedback_value`)
        feedback_value.innerHTML = data.total_feedback_value
        let upvote = document.getElementById(`upvote-btn`)
        let downvote = document.getElementById(`downvote-btn`)
        if (data.message === 'upvote') {
            upvote.classList.add('react-choice')
            downvote.classList.remove('react-choice')
        } else if (data.message === 'downvote') {
            upvote.classList.remove('react-choice')
            downvote.classList.add('react-choice')
        } else if (data.message === 'deleted') {
            upvote.classList.remove('react-choice')
            downvote.classList.remove('react-choice')
        }
    } else {
        errorNotification({
            title: 'Lỗi',
            message: 'Bạn cần đăng nhập',
        });
    }
}
