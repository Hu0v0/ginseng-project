/**
 * 全局后端接口地址配置
 * ------------------------------------------------------------------
 * 本地开发：自动使用 http://127.0.0.1:8000（无需改动）
 * 云端部署：把 CLOUD_API 改成你后端服务的公网地址，例如
 *     https://ginseng-api.onrender.com
 *     https://xxx.up.railway.app
 *   —— 填好后，GitHub Pages 等静态托管的前端也能跨域连上后端
 *   （后端已开启 CORS，允许任意来源跨域访问）
 * 若前后端部署在同一个域名下（如 Nginx 反代 /api），保持 CLOUD_API
 * 为空字符串，前端将使用相对路径（同源请求）。
 * ------------------------------------------------------------------
 */
(function () {
    var CLOUD_API = ''; // ← 云端部署时在这里填写后端公网地址
    var isLocal = ['127.0.0.1', 'localhost', '::1'].indexOf(window.location.hostname) !== -1;
    window.API_BASE = CLOUD_API || (isLocal ? 'http://127.0.0.1:8000' : '');
})();
