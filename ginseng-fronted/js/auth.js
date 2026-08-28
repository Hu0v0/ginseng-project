/**
 * 全站登录状态公共脚本
 * 作用：
 *   1. 根据 localStorage.currentUser 渲染导航栏右上角（登录/注册 ↔ 你好+退出+后台入口）
 *   2. 提供 GinsengAuth.getUser() / requireLogin() 给业务按钮（如"立即预约"）调用
 *
 * 使用方式：在页面导航栏右上角容器上加 id="authArea"，并在 </body> 前引入：
 *   <script src="js/auth.js"></script>
 */
(function () {
    // 读取当前登录用户，解析失败或未登录返回 null
    function getUser() {
        try {
            const u = JSON.parse(localStorage.getItem('currentUser'));
            return (u && u.username) ? u : null;
        } catch (e) {
            return null;
        }
    }

    // 退出登录
    function logout() {
        localStorage.removeItem('currentUser');
        location.reload();
    }

    // 渲染导航栏右上角
    function renderAuthArea() {
        const authArea = document.getElementById('authArea');
        if (!authArea) return;
        const user = getUser();

        if (user) {
            // 管理员显示"后台管理"入口；普通用户显示"我的预约"入口
            const entryBtn = user.role === 'admin'
                ? '<a href="admin.html"><button class="btn btn-primary btn-sm">后台管理</button></a>'
                : '<a href="my-orders.html"><button class="btn btn-default btn-sm">我的预约</button></a>';
            authArea.innerHTML =
                '<span style="color: var(--text-secondary); font-size: 14px;">你好，' +
                '<strong style="color: var(--primary-color);">' + user.username + '</strong></span>' +
                entryBtn +
                '<button class="btn btn-default btn-sm" id="__logoutBtn">退出登录</button>';
            const btn = document.getElementById('__logoutBtn');
            if (btn) btn.addEventListener('click', logout);
        } else {
            // 未登录：统一的登录 / 注册按钮
            authArea.innerHTML =
                '<a href="login.html"><button class="btn btn-default btn-sm">登录</button></a>' +
                '<a href="register.html"><button class="btn btn-primary btn-sm">注册</button></a>';
        }
    }

    /**
     * 需要登录才能进行的操作。
     * 已登录：执行 onOk 回调（不传则原地不动）。
     * 未登录：提示后跳转登录页，并记录来源页，登录后可回跳。
     */
    function requireLogin(onOk, tipText) {
        const user = getUser();
        if (user) {
            if (typeof onOk === 'function') onOk(user);
            return true;
        }
        alert(tipText || '请先登录后再进行此操作，即将跳转到登录页');
        // 记录来源，登录成功后可回跳（login.html 已支持读取）
        try { sessionStorage.setItem('redirectAfterLogin', location.pathname.split('/').pop()); } catch (e) {}
        window.location.href = 'login.html';
        return false;
    }

    // 暴露到全局，供页面业务调用
    window.GinsengAuth = { getUser: getUser, logout: logout, requireLogin: requireLogin };

    // DOM 就绪后自动渲染导航栏
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', renderAuthArea);
    } else {
        renderAuthArea();
    }
})();
