$(document).ready(function () {
    $('#searchInput').typeahead({
        source: function (query, process) {
            // Gửi yêu cầu AJAX đến server để lấy gợi ý dựa trên từ khóa query
            $.ajax({
                url: '/get_suggestions', // Đường dẫn đến endpoint Flask của bạn
                type: 'GET',
                data: { term: query },
                dataType: 'json',
                success: function (data) {
                    process(data.results);
                }
            });
        },
        minLength: 2, // Số ký tự tối thiểu trước khi gợi ý bắt đầu
        items: 'all', // Hiển thị tất cả các kết quả gợi ý
        afterSelect: function (item) {
            // Sau khi chọn gợi ý, điền vào input và kích hoạt sự kiện tab
            this.$element.val(item);
            this.$element.trigger('keydown.tab');
            $('#searchInput').typeahead('close');
        }
    });
});