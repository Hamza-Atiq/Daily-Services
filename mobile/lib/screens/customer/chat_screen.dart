import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ApiService _api = ApiService();
  final List<_ChatMessage> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Add welcome message
    _messages.add(_ChatMessage(
      text: "Assalam-o-Alaikum! \u{1F44B}\n\n"
          "Main aapka **Service Assistant** hoon.\n"
          "Mujhe batayein aapko kaunsi service chahiye?\n\n"
          "\u{1F527} AC Repair \u{1F6BF} Plumbing \u{26A1} Electrical\n"
          "\u{1F9F9} Cleaning \u{1F4DA} Tutoring \u{1F697} Mechanic\n"
          "\u{1F484} Beauty \u{1F3A8} Painting \u{1FA9A} Carpentry\n\n"
          "You can message in **English, Urdu, or Roman Urdu** \u{2014} whatever is comfortable!",
      isUser: false,
      trace: null,
    ));
  }

  void _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isLoading) return;

    setState(() {
      _messages.add(_ChatMessage(text: text, isUser: true, trace: null));
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    final response = await _api.sendMessage(text);

    setState(() {
      _isLoading = false;
      _messages.add(_ChatMessage(
        text: response['response'] ?? 'No response received.',
        isUser: false,
        trace: response['trace'] as List<dynamic>?,
      ));
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.heroGradient),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              Expanded(child: _buildMessageList()),
              if (_isLoading) _buildTypingIndicator(),
              _buildInputBar(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        border: Border(bottom: BorderSide(color: AppTheme.border.withValues(alpha: 0.3))),
      ),
      child: Row(
        children: [
          Container(
            width: 40, height: 40,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.support_agent, color: Colors.white, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Service Assistant', style: Theme.of(context).textTheme.titleMedium),
                Row(
                  children: [
                    Container(
                      width: 8, height: 8,
                      decoration: BoxDecoration(
                        color: AppTheme.primary,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text('Online - 8 agents ready',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.primary)),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.textMuted),
            onPressed: () {
              setState(() {
                _messages.clear();
                _messages.add(_ChatMessage(
                  text: "Session reset! How can I help you? \u{1F3E0}",
                  isUser: false,
                  trace: null,
                ));
              });
              _api.resetSession();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMessageList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final msg = _messages[index];
        return _ChatBubble(message: msg, index: index);
      },
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: AppTheme.glassCard,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 20, height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: AppTheme.primary.withValues(alpha: 0.7),
                  ),
                ),
                const SizedBox(width: 10),
                Text('AI is thinking...',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.primary)),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms).slideY(begin: 0.2);
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        border: Border(top: BorderSide(color: AppTheme.border.withValues(alpha: 0.3))),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppTheme.surfaceLight,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppTheme.border.withValues(alpha: 0.2)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      style: const TextStyle(color: AppTheme.textPrimary, fontSize: 15),
                      decoration: const InputDecoration(
                        hintText: 'Type your service request...',
                        hintStyle: TextStyle(color: AppTheme.textMuted),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                      maxLines: null,
                      textInputAction: TextInputAction.send,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primary.withValues(alpha: 0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Icon(
                _isLoading ? Icons.hourglass_top_rounded : Icons.send_rounded,
                color: Colors.white,
                size: 20,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Chat Message Model ──────────────────────────────────────────────
class _ChatMessage {
  final String text;
  final bool isUser;
  final List<dynamic>? trace;

  _ChatMessage({required this.text, required this.isUser, this.trace});
}

// ── Chat Bubble Widget ──────────────────────────────────────────────
class _ChatBubble extends StatefulWidget {
  final _ChatMessage message;
  final int index;

  const _ChatBubble({required this.message, required this.index});

  @override
  State<_ChatBubble> createState() => _ChatBubbleState();
}

class _ChatBubbleState extends State<_ChatBubble> {
  bool _showTrace = false;

  @override
  Widget build(BuildContext context) {
    final msg = widget.message;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: msg.isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: msg.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (!msg.isUser) ...[
                Container(
                  width: 32, height: 32,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.smart_toy_rounded, color: Colors.white, size: 18),
                ),
                const SizedBox(width: 8),
              ],
              Flexible(
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: msg.isUser ? AppTheme.primary.withValues(alpha: 0.15) : AppTheme.card,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(16),
                      topRight: const Radius.circular(16),
                      bottomLeft: Radius.circular(msg.isUser ? 16 : 4),
                      bottomRight: Radius.circular(msg.isUser ? 4 : 16),
                    ),
                    border: Border.all(
                      color: msg.isUser
                          ? AppTheme.primary.withValues(alpha: 0.3)
                          : AppTheme.border.withValues(alpha: 0.2),
                    ),
                  ),
                  child: msg.isUser
                      ? Text(msg.text, style: const TextStyle(color: AppTheme.textPrimary, fontSize: 15))
                      : MarkdownBody(
                          data: msg.text,
                          styleSheet: MarkdownStyleSheet(
                            p: const TextStyle(color: AppTheme.textPrimary, fontSize: 14, height: 1.5),
                            strong: const TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.w600),
                            h1: const TextStyle(color: AppTheme.textPrimary, fontSize: 18, fontWeight: FontWeight.w700),
                            h2: const TextStyle(color: AppTheme.textPrimary, fontSize: 16, fontWeight: FontWeight.w600),
                            code: TextStyle(
                              color: AppTheme.accent,
                              backgroundColor: AppTheme.surfaceLight.withValues(alpha: 0.5),
                              fontSize: 13,
                            ),
                            codeblockDecoration: BoxDecoration(
                              color: AppTheme.surfaceLight,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            listBullet: const TextStyle(color: AppTheme.primary),
                          ),
                        ),
                ),
              ),
              if (msg.isUser) ...[
                const SizedBox(width: 8),
                Container(
                  width: 32, height: 32,
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceLight,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.person_rounded, color: AppTheme.textSecondary, size: 18),
                ),
              ],
            ],
          ),
          // Trace toggle
          if (!msg.isUser && msg.trace != null && msg.trace!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Padding(
              padding: const EdgeInsets.only(left: 40),
              child: GestureDetector(
                onTap: () => setState(() => _showTrace = !_showTrace),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.info.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.info.withValues(alpha: 0.2)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _showTrace ? Icons.visibility_off : Icons.visibility,
                        color: AppTheme.info,
                        size: 14,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _showTrace ? 'Hide Reasoning' : 'Show Reasoning (${msg.trace!.length} steps)',
                        style: const TextStyle(color: AppTheme.info, fontSize: 11, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            if (_showTrace) _buildTraceView(msg.trace!),
          ],
        ],
      ),
    ).animate().fadeIn(duration: 300.ms, delay: Duration(milliseconds: widget.index > 0 ? 100 : 0)).slideY(begin: 0.1);
  }

  Widget _buildTraceView(List<dynamic> trace) {
    return Padding(
      padding: const EdgeInsets.only(left: 40, top: 6),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppTheme.surfaceLight.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.info.withValues(alpha: 0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Agent Trace', style: TextStyle(color: AppTheme.info, fontSize: 12, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            ...trace.map((step) {
              final isToolCall = step['type'] == 'tool_call';
              return Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      isToolCall ? Icons.build_circle : Icons.check_circle,
                      color: isToolCall ? AppTheme.accent : AppTheme.primary,
                      size: 14,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        isToolCall
                            ? '${step['agent'] ?? 'agent'} called ${step['tool'] ?? 'tool'}'
                            : '${step['agent'] ?? 'agent'}: response received',
                        style: const TextStyle(color: AppTheme.textSecondary, fontSize: 11),
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 200.ms);
  }
}
